import requests
from Crypto.Cipher import AES
from Crypto.Util import Counter
from crypto import (base64_to_a32, base64_url_decode, decrypt_attr, a32_to_str)
import json
from locales import *
from exceptions import *
import logging
import random
import re
import os
import threading
import time


CHUNK_SIZE = 32768  # 32 Kb
# Connect/read timeout: without it a stalled host hangs the updater forever
# behind a "do not close this window" dialog.
TIMEOUT = (10, 60)

class Cancellation():
    """Pause/cancel signal shared by the downloaders. resume is set while
    downloading may proceed; kill is set once the user cancels."""
    def __init__(self):
        self.resume = threading.Event()
        self.resume.set()
        self.kill = threading.Event()

    def set_wait(self, wait):
        self.resume.clear() if wait else self.resume.set()

    def set_kill(self, kill):
        if kill:
            self.kill.set()
            self.resume.set()  # release a paused download so it can bail out

    def cancelled(self):
        """Block while paused. True if the download was cancelled."""
        self.resume.wait()
        return self.kill.is_set()

class Download():
    def __init__(self, app, path, temp_path, language='en'):
        self.app = app
        self.path = os.path.join(path, temp_path)
        self.language = language
        self.signal = Cancellation()
        self.mega = None

    def set_wait(self, wait):
        self.signal.set_wait(wait)

    def set_kill(self, kill):
        self.signal.set_kill(kill)

    def start_download(self, url):
        host = None
        try:
            host = self.get_file_host(url)

            if host == Host.MEGA:
                self.mega = self._MegaDownload(self.app, self.signal, self.language)
                self.mega.download_url(url, self.path)
            elif host == Host.DROPBOX:
                self._download_from_dropbox(url)
            elif host == Host.GITHUB:
                self._download_from_github(url)
            else:
                raise Exception(ExceptionMessage.NO_FILE_HOST[self.language])
        except ConnectionResetError:
            if host == Host.MEGA:
                raise Exception(ExceptionMessage.DOWNLOAD_ERROR_MEGA[self.language])
            else:
                raise Exception(ExceptionMessage.DOWNLOAD_ERROR[self.language])
        except BandwithExceededError:
            raise BandwithExceededError
        except Exception as e:
            raise e

    # Every host listed here must have a branch in start_download, or the player
    # gets offered a host that always fails.
    def get_file_host(self, url):
        if "mega.nz" in url:
            return Host.MEGA
        elif "dropbox.com" in url:
            return Host.DROPBOX
        elif "github.com" in url:
            return Host.GITHUB
        else:
            raise Exception(ExceptionMessage.NO_FILE_HOST[self.language])

    def _stream_to_file(self, filename, response):
        content_length = response.headers.get("content-length")
        if not content_length: raise Exception(ExceptionMessage.NO_VALID_FILE_FOUND[self.language])
        total = int(content_length)
        written = 0
        last_percentage = -1
        with open(filename, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if self.signal.cancelled():
                    return
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    written += len(chunk)
                    percentage = round(written / total * 100)
                    if percentage != last_percentage:
                        last_percentage = percentage
                        self.app.set_note(str(percentage) + "%")
                        self.app.set_progress(percentage / 100)

    def _finish(self):
        self.app.set_note("100%")
        self.app.set_progress(1)

    def _download_from_github(self, url):
        filename = os.path.join(self.path, url.split("/")[-1])
        response = requests.get(url, stream=True, timeout=TIMEOUT)
        self._stream_to_file(filename, response)
        self._finish()

    # Dropbox
    def _download_from_dropbox(self, url):
        if 'dl=' in url:
            url = url.replace('dl=0', 'dl=1')
        else:
            url += '&dl=1'

        response = requests.get(url, stream=True, timeout=TIMEOUT)
        filename = os.path.join(self.path, url.split('/')[6].split('?')[0])
        self._stream_to_file(filename, response)
        self._finish()

    # Mega
    class _MegaDownload():
        def __init__(self, app, signal, language='en'):
            self.app = app
            self.signal = signal
            self.language = language
            self.sequence_num = random.randint(0, 0xFFFFFFFF)
            self.timeout = 160  # max secs to wait for resp from api requests
            self.schema = 'https'
            self.domain = 'mega.co.nz'
            # Public links need no session, so there is no login: this class talks to
            # the Mega API directly and the mega.py package is not needed at all.
            self.sid = None

        def download_url(self, url, dest_path=None, dest_filename=None):
            path = self._parse_url(url).split('!')
            file_id = path[0]
            file_key = path[1]
            return self._download_file(
                file_handle=file_id,
                file_key=file_key,
                dest_path=dest_path,
                dest_filename=dest_filename,
                is_public=True,
            )

        def _api_request(self, data):
            # ponytail: replaced tenacity @retry(wait_exponential(2,min=2,max=60))
            # on RuntimeError; bounded to 6 attempts matching the old ceiling.
            for attempt in range(6):
                try:
                    return self._api_request_once(data)
                except RuntimeError:
                    if attempt == 5:
                        raise
                    time.sleep(min(2 * 2 ** attempt, 60))

        def _api_request_once(self, data):
            params = {'id': self.sequence_num}
            self.sequence_num += 1

            if self.sid:
                params.update({'sid': self.sid})

            # ensure input data is a list
            if not isinstance(data, list):
                data = [data]

            url = f'{self.schema}://g.api.{self.domain}/cs'
            response = requests.post(
                url,
                params=params,
                data=json.dumps(data),
                timeout=self.timeout,
            )
            json_resp = json.loads(response.text)
            try:
                if isinstance(json_resp, list):
                    int_resp = json_resp[0] if isinstance(json_resp[0], int) else None
                elif isinstance(json_resp, int):
                    int_resp = json_resp
            except IndexError:
                int_resp = None
            if int_resp is not None:
                if int_resp == 0:
                    return int_resp
                if int_resp == -3:
                    logging.info("Mega request failed, retrying")
                logging.info("Mega API response: %s", int_resp)
            return json_resp[0]
        
        def _download_file(self, file_handle, file_key, dest_path=None, dest_filename=None, is_public=False, file=None):
            if file is None:
                if is_public:
                    file_key = base64_to_a32(file_key)
                    file_data = self._api_request({
                        'a': 'g',
                        'g': 1,
                        'p': file_handle
                    })
                else:
                    file_data = self._api_request({
                        'a': 'g',
                        'g': 1,
                        'n': file_handle
                    })

                k = (file_key[0] ^ file_key[4], file_key[1] ^ file_key[5],
                    file_key[2] ^ file_key[6], file_key[3] ^ file_key[7])
                iv = file_key[4:6] + (0, 0)
            else:
                file_data = self._api_request({'a': 'g', 'g': 1, 'n': file['h']})
                k = file['k']
                iv = file['iv']

            if 'g' not in file_data:
                raise Exception(ExceptionMessage.FILE_NOT_ACCESSIBLE[self.language])
            file_url = file_data['g']
            file_size = file_data['s']
            attribs = base64_url_decode(file_data['at'])
            attribs = decrypt_attr(attribs, k)

            if dest_filename is not None:
                file_name = dest_filename
            else:
                file_name = attribs['n']

            response = requests.get(file_url, stream=True, timeout=TIMEOUT)

            if response.status_code == 509:
                raise BandwithExceededError()

            if dest_path is None:
                dest_path = ''
            else:
                dest_path += '/'
            filepath = os.path.join(dest_path, file_name)
            written = 0
            last_percentage = -1
            with open(filepath, "wb") as f:
                k_str = a32_to_str(k)
                counter = Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64)
                aes = AES.new(k_str, AES.MODE_CTR, counter=counter)

                for chunk in response.iter_content(CHUNK_SIZE):
                    chunk = aes.decrypt(chunk)
                    if self.signal.cancelled():
                        return
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        written += len(chunk)
                        percentage = round(written / int(file_size) * 100)
                        if percentage != last_percentage:
                            last_percentage = percentage
                            self.app.set_note(str(percentage) + "%")
                            self.app.set_progress(percentage / 100)
            return filepath

        def _parse_url(self, url):
            """Parse file id and key from url."""
            if '/file/' in url:
                # V2 URL structure
                url = url.replace(' ', '')
                file_id = re.findall(r'\W\w\w\w\w\w\w\w\w\W', url)[0][1:-1]
                id_index = re.search(file_id, url).end()
                key = url[id_index + 1:]
                return f'{file_id}!{key}'
            elif '!' in url:
                # V1 URL structure
                match = re.findall(r'/#!(.*)', url)
                path = match[0]
                return path
            else:
                raise Exception(ExceptionMessage.NO_FILE_HOST[self.language])
            