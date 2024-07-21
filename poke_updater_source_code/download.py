import requests
from mega import Mega
from Crypto.Cipher import AES
from Crypto.Util import Counter
from crypto import (base64_to_a32, base64_url_decode, decrypt_attr, a32_to_str)
import json
from locales import *
from bs4 import BeautifulSoup
from tenacity import retry, wait_exponential, retry_if_exception_type
import random
import re
import os


CHUNK_SIZE = 32768  # 32 Kb
wait, kill = False, False

class Download():
    def __init__(self, app, path, temp_path, language='en'):
        self.app = app
        self.path = os.path.join(path, temp_path)
        self.language = language
        self.wait = False
        self.kill = False
        self.mega = None
        
    def set_wait(self, wait):
        self.wait = wait
        if self.mega:
            self.mega.set_wait(wait)
    def set_kill(self, kill):
        self.kill = kill
        if self.mega:
            self.mega.set_kill(kill)

    def start_download(self, url):
        host = None
        try:
            host = self.get_file_host(url)
            
            if host == Host.MEGA:
                self.mega = self._MegaDownload(self.app)
                self.mega.download_url(url, self.path)
            # elif host == Host.GOOGLE_DRIVE:
            #     self._download_file_from_google_drive(url)
            elif host == Host.MEDIAFIRE:
                download_url = BeautifulSoup(requests.get(url).content, 'html.parser').find(id="downloadButton")["href"]
                self._download_from_mediafire(download_url)
            elif host == Host.DROPBOX:
                self._download_from_dropbox(url)
            else:
                raise Exception(ExceptionMessage.NO_FILE_HOST)
        except ConnectionResetError:
            if host == Host.MEGA:
                raise Exception(ExceptionMessage.DOWNLOAD_ERROR_MEGA[self.language])
            else:
                raise Exception(ExceptionMessage.DOWNLOAD_ERROR[self.language])
        except Exception as e:
            raise e

    def get_file_host(self, url):
        if "mega.nz" in url:
            return Host.MEGA
        # elif "drive.google.com" in url:
        #     return Host.GOOGLE_DRIVE
        elif "mediafire.com" in url:
            return Host.MEDIAFIRE
        elif "anonfiles.com" in url:
            return Host.ANONFILES
        elif "dropbox.com" in url:
            return Host.DROPBOX
        else:
            raise Exception(ExceptionMessage.NO_FILE_HOST[self.language])

    def _stream_to_file(self, filename, response):
        content_length = response.headers.get("content-length")
        if not content_length: raise Exception(ExceptionMessage.NO_VALID_FILE_FOUND[self.language])
        with open(filename, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                while self.wait:
                    if self.kill:
                        return
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    current_size=os.path.getsize(filename) 
                    percentage=round((int(current_size)/int(content_length))*100)
                    self.app.progress_label.configure(text=str(percentage) + "%")
                    self.app.progressbar.set(percentage / 100)

    # Mediafire
    def _download_from_mediafire(self, url):
        filename = url.split("/")[-1].replace('+', ' ')
        content = requests.get(url, stream=True)
        filename = os.path.join(self.path, filename)
        self._stream_to_file(filename, content)
        self.app.progress_label.configure(text="100%")
        self.app.progressbar.set(1)

    # Dropbox
    def _download_from_dropbox(self, url):
        if 'dl=' in url:
            url = url.replace('dl=0', 'dl=1')
        else:
            url += '&dl=1'            
        
        content = requests.get(url, stream=True)
        filename = os.path.join(self.path, url.split('/')[6].split('?')[0])
        self._stream_to_file(filename, content)
        self.app.progress_label.configure(text="100%")
        self.app.progressbar.set(1)
    
    # Google Drive
    def _download_file_from_google_drive(self, url):
            URL = "https://docs.google.com/uc?export=download&confirm=1"
            session = requests.Session()
            id = self._gdrive_get_id_from_url(url)
            response = session.get(URL, params={"id": id}, stream=True)
            token = self._gdrive_get_confirm_token(response)
            if token:
                params = {"id": id, "confirm": token}
                response = session.get(URL, params=params, stream=True)
            if response.status_code == 200:
                self._gdrive_save_response_content(response, self.path)
            elif response.status_code == 404 :
                raise Exception(ExceptionMessage.FILE_NOT_ACCESSIBLE[self.language])
            else:
                raise Exception(ExceptionMessage.DOWNLOAD_ERROR[self.language])

    def _gdrive_get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value
        return None

    def _gdrive_get_id_from_url(self, url):
        id = url.split("/")[5]
        return id

    def _gdrive_save_response_content(self, response, destination):
        content_disposition = response.headers.get("content-disposition")
        filename = re.findall("filename=(.+)", content_disposition)[0].split(';')[0].replace('"', '')
        filename = os.path.join(destination, filename)
        self._stream_to_file(filename, response)
        if self.kill:
            return
        self.app.progress_label.configure(text="100%")
        self.app.progressbar.set(1)

    # Mega
    class _MegaDownload():
        def __init__(self, app):
            self.app = app
            self.sequence_num = random.randint(0, 0xFFFFFFFF)
            self.timeout = 160  # max secs to wait for resp from api requests
            self.schema = 'https'
            self.domain = 'mega.co.nz'
            self.sid = None
            self.mega = Mega()
            self.mega.login()
            self.wait = False
            self.kill = False
            
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
        
        def set_wait(self, wait):
            self.wait = wait
        def set_kill(self, kill):
            self.kill = kill

        @retry(retry=retry_if_exception_type(RuntimeError),
        wait=wait_exponential(multiplier=2, min=2, max=60))
        def _api_request(self, data):
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
                    msg = 'Request failed, retrying'
                    print(msg)
                print(int_resp)
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
                print('File not accessible anymore')
            file_url = file_data['g']
            file_size = file_data['s']
            attribs = base64_url_decode(file_data['at'])
            attribs = decrypt_attr(attribs, k)

            if dest_filename is not None:
                file_name = dest_filename
            else:
                file_name = attribs['n']

            response = requests.get(file_url, stream=True)

            if dest_path is None:
                dest_path = ''
            else:
                dest_path += '/'
            filepath = os.path.join(dest_path, file_name)
            with open(filepath, "wb") as f:
                k_str = a32_to_str(k)
                counter = Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64)
                aes = AES.new(k_str, AES.MODE_CTR, counter=counter)

                for chunk in response.iter_content(CHUNK_SIZE): #chunk_start, chunk_size in get_chunks(file_size):
                    #chunk = input_file.read(chunk_size)
                    chunk = aes.decrypt(chunk)
                    while self.wait:
                        if self.kill:
                            return
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        current_size=os.path.getsize(filepath) 
                        percentage=round((int(current_size)/int(file_size))*100)
                        self.app.progress_label.configure(text=str(percentage) + "%")
                        self.app.progressbar.set(percentage / 100)

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
                print('Url key missing')
            