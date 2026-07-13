import os
from time import sleep
import sys
import io
import requests
import tkinter as tk
import shutil
import pathlib
from locales import *
from exceptions import *
import locale
from download import Download
from patoolib import extract_archive
import zipfile
from reversal import Reversal
import customtkinter
import subprocess
import logging
import threading
import queue
import re

IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    import ctypes
    import winsound

# resume is set while the worker may run; kill is set when the user cancels.
# not_extracting is cleared only while an archive is being extracted.
resume = threading.Event()
resume.set()
kill = threading.Event()
not_extracting = threading.Event()
not_extracting.set()

def cancelled():
    """Block while the update is paused. True if the user cancelled."""
    resume.wait()
    return kill.is_set()

download_hosts = {}
# Determine if application is a script file or exe
if getattr(sys, 'frozen', False):
    REAL_PATH = os.path.dirname(os.path.dirname(sys.executable))
elif __file__:
    REAL_PATH = os.path.dirname(__file__)

TEST_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
test = False
path_to_use = TEST_PATH if test else REAL_PATH

def get_user_language():
    if IS_WINDOWS:
        user_locale = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()].lower()
    else:
        # getdefaultlocale is deprecated and goes away in 3.15; read the env directly.
        # e.g. "es_ES.UTF-8" -> es. Unset under the C locale, hence the fallback.
        env_locale = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or ""
        user_locale = env_locale.split(".")[0].lower() or "en_us"
    return user_locale.split("_")[0]

LANGUAGE = get_user_language()
# Not every language the OS may report is translated (Linux especially)
if LANGUAGE not in ExceptionMessage.CLOSE_WINDOW:
    LANGUAGE = 'en'

SETTINGS_FILE = "pu_config"
TEMP_PATH = "temp"
current_step = None
download = None

LOG_FILE = "updater.log"

# Frozen builds run windowed: sys.stdout is None, so print() swallows every error.
logging.basicConfig(
    filename=os.path.join(path_to_use, LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

# Game.exe on Windows, Game_Linux (or plain Game) on the Linux builds. Matched by
# full name, not by stem: Game.ini and Game.rgssad are data, not the executable.
GAME_EXECUTABLES = ("game.exe", "game_linux", "game_linux.sh", "game.sh", "game")

def find_game_exe_recursive(root_path):
    """
    Recursively search for the game executable in the directory structure.
    Returns the directory containing it, or None if not found.
    """
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.lower() in GAME_EXECUTABLES:
                return root
    return None

def find_game_executable(root_path):
    """Full path of the game binary, or None. Prefers the one matching this OS, so a
    zip carrying both Game.exe and Game_Linux relaunches the right one."""
    game_dir = find_game_exe_recursive(root_path)
    if not game_dir:
        return None
    candidates = [f for f in os.listdir(game_dir) if f.lower() in GAME_EXECUTABLES]
    if not candidates:
        return None
    return os.path.join(game_dir, sorted(candidates, key=lambda f: f.lower().endswith(".exe") != IS_WINDOWS)[0])

def make_game_executable(game_path):
    """Restore the +x bit that zip archives don't carry, so the Linux build of
    the game (and its shell launchers) can actually be run."""
    game_dir = find_game_exe_recursive(game_path)
    if not game_dir:
        return
    for file in os.listdir(game_dir):
        path = os.path.join(game_dir, file)
        if not os.path.isfile(path):
            continue
        if file.lower() in GAME_EXECUTABLES or file.endswith(".sh"):
            os.chmod(path, os.stat(path).st_mode | 0o111)

def should_ignore_folder(folder_name, folder_path, ignored_folders):
    """
    Check if a folder should be ignored based on the ignored folders list.

    Matches whole path components: an ignored folder named "Data" protects
    <game>/Data, not <game>/Graphics/Data_old or a folder called "Database".

    Args:
        folder_name: Name of the folder
        folder_path: Full path of the folder
        ignored_folders: List of folder names to ignore

    Returns:
        bool: True if the folder should be ignored, False otherwise
    """
    parts = {part.lower() for part in pathlib.Path(folder_path).parts}
    parts.add(folder_name.lower())
    return any(ignored.lower() in parts for ignored in ignored_folders)

def handle_complex_directory_structure(extracted_path, destination_path, ignored_folders=None):
    """
    Handle complex directory structures where Game.exe might be nested.
    Accounts for the fact that the updater runs from inside the game directory.
    
    Args:
        extracted_path: Path to extracted files
        destination_path: Destination path for files
        ignored_folders: List of folder names to ignore (default: ["Fotos"])
    """
    if ignored_folders is None:
        ignored_folders = ["Fotos"]
    
    # First, verify that Game.exe exists somewhere in the structure
    game_exe_dir = find_game_exe_recursive(extracted_path)
    
    if not game_exe_dir:
        return False, None
    
    poke_updater_from_zip = None
    
    # Get the name of the directory containing Game.exe
    game_dir_name = os.path.basename(game_exe_dir)
    
    # Get parent directory (where sibling folders should go)
    parent_destination = os.path.dirname(destination_path)
    
    # Process all items in the extracted path
    for item in os.listdir(extracted_path):
        src_item = os.path.join(extracted_path, item)
        
        # Skip hidden files except .nomedia
        if item.startswith(".") and item != ".nomedia":
            continue
        
        # Skip git files
        if '.git' in item:
            continue
        
        # Skip temp directory
        if item == TEMP_PATH:
            continue
        
        # Skip ignored folders to keep current user data
        if should_ignore_folder(item, src_item, ignored_folders):
            continue

        # Handle directories
        if os.path.isdir(src_item):
            # Check if this is a poke_updater directory - save path for batch file
            if "poke_updater" in item:
                poke_updater_from_zip = src_item
                continue

            # Check if this is the directory containing Game.exe
            if item == game_dir_name and src_item == game_exe_dir:
                # Copy contents of this directory to the current destination (where updater runs)
                for root, dirs, files in os.walk(src_item):
                    # Calculate relative path from the game directory
                    rel_path = os.path.relpath(root, src_item)
                    
                    # Determine destination directory
                    if rel_path == '.':
                        dst_dir = destination_path
                    else:
                        dst_dir = os.path.join(destination_path, rel_path)
                        os.makedirs(dst_dir, exist_ok=True)
                    
                    # Process files
                    for file in files:
                        # Skip hidden files except .nomedia
                        if file.startswith(".") and file != ".nomedia":
                            continue
                        
                        # Skip git files
                        if '.git' in file:
                            continue

                        # Skip files in ignored folders to keep current user data
                        if should_ignore_folder(os.path.basename(root), root, ignored_folders):
                            continue
                        
                        src_file = os.path.join(root, file)
                        
                        # Handle poke_updater files specially - but don't overwrite directory path
                        if "poke_updater" in file:
                            # Only set poke_updater_from_zip if it's not already set to a directory
                            if not poke_updater_from_zip or not os.path.isdir(poke_updater_from_zip):
                                # Set to the parent directory of the file, not the file itself
                                poke_updater_from_zip = os.path.dirname(src_file)
                            continue
                        
                        dst_file = os.path.join(dst_dir, file)
                        
                        # Skip updating poke_updater directory contents during move phase
                        # These will be handled by the batch file after the process exits
                        if "poke_updater" in dst_file:
                            continue
                        
                        # Remove destination file if it exists (for replacement)
                        if os.path.exists(dst_file):
                            if os.path.isdir(dst_file):
                                shutil.rmtree(dst_file)
                            else:
                                os.remove(dst_file)
                        
                        # Move the file
                        shutil.move(src_file, dst_file)
            else:
                # This is a sibling directory - copy it to the parent directory
                dst_item = os.path.join(parent_destination, item)
                
                # Skip poke_updater directories - they will be handled by batch file
                if "poke_updater" in item:
                    continue

                # Skip ignored folders to keep current user data
                if should_ignore_folder(item, src_item, ignored_folders):
                    continue
                
                # Remove destination directory if it exists
                if os.path.exists(dst_item):
                    shutil.rmtree(dst_item)
                
                # Move the directory
                shutil.move(src_item, dst_item)
        
        elif os.path.isfile(src_item):
            # Handle individual files at root level
            if "poke_updater" in item:
                # Only set poke_updater_from_zip if it's not already set to a directory
                if not poke_updater_from_zip or not os.path.isdir(poke_updater_from_zip):
                    # Set to the parent directory of the file, not the file itself
                    poke_updater_from_zip = os.path.dirname(src_item)
                continue

            # Skip files that might be in ignored folders (though files at root level are unlikely to be in ignored folders)
            # This is mainly for completeness
            if should_ignore_folder(item, src_item, ignored_folders):
                continue
            
            # Copy file to parent directory (as a sibling to the game directory)
            dst_item = os.path.join(parent_destination, item)
            
            # Remove destination file if it exists
            if os.path.exists(dst_item):
                os.remove(dst_item)
            
            # Move the file
            shutil.move(src_item, dst_item)
    
    return True, poke_updater_from_zip

def remove_updater(poke_updater_from_zip):
    temp_path = os.path.join(path_to_use, TEMP_PATH)
    poke_updater_dir = os.path.join(path_to_use, 'poke_updater')

    # Relaunch the game as the LAST step of the cleanup script: only once the updater
    # has been replaced and temp is gone, so the game never starts on half-moved files.
    game_exe = find_game_executable(path_to_use)
    if not game_exe:
        logging.warning("Game executable not found: the player will have to start it")

    # The updater can't replace or delete its own running files, so hand the last
    # steps to a detached script that waits for this process to exit first.
    if IS_WINDOWS:
        ROBOCOPY_PARAMS = "/e /dcopy:da /ns /nc /nfl /ndl /np /njh /njs"
        copy_updater = "" if not poke_updater_from_zip else f"""
if exist "{poke_updater_from_zip}" (
    if not exist "{poke_updater_dir}" mkdir "{poke_updater_dir}" >nul 2>&1

    REM Copy with single retry
    robocopy "{poke_updater_from_zip}" "{poke_updater_dir}" {ROBOCOPY_PARAMS} >nul 2>&1
    if errorlevel 8 (
        timeout /t 1 /nobreak >nul
        robocopy "{poke_updater_from_zip}" "{poke_updater_dir}" {ROBOCOPY_PARAMS} >nul 2>&1
    )
)
"""
        launch_game = "" if not game_exe else f"""
REM Relaunch the game from its own folder, so relative paths resolve
cd /d "{os.path.dirname(game_exe)}"
start "" "{os.path.basename(game_exe)}"
"""
        script = f"""@echo off
timeout /t 3 /nobreak >nul
taskkill /f /im poke_updater.exe >nul 2>&1
{copy_updater}
REM Clean up temporary files
if exist "{temp_path}" rmdir /s /q "{temp_path}" >nul 2>&1
{launch_game}
REM Self-destruct
timeout /t 1 /nobreak >nul
del "%~f0" >nul 2>&1
"""
        script_path = os.path.join(path_to_use, 'cleanup.bat')
        with open(script_path, 'w', encoding='cp1252') as f:
            f.write(script)
        # CREATE_NO_WINDOW: don't flash a console window at the player
        command = ['cmd.exe', '/c', script_path]
        kwargs = {'creationflags': 0x08000000}
    else:
        copy_updater = "" if not poke_updater_from_zip else f"""
if [ -d "{poke_updater_from_zip}" ]; then
    mkdir -p "{poke_updater_dir}"
    cp -rf "{poke_updater_from_zip}/." "{poke_updater_dir}/" >/dev/null 2>&1 || \
        (sleep 1; cp -rf "{poke_updater_from_zip}/." "{poke_updater_dir}/" >/dev/null 2>&1)
    chmod +x "{poke_updater_dir}"/* >/dev/null 2>&1
fi
"""
        # setsid: the game must outlive this script, which deletes itself right after
        launch_game = "" if not game_exe else f"""
cd "{os.path.dirname(game_exe)}"
chmod +x "{game_exe}" >/dev/null 2>&1
setsid "./{os.path.basename(game_exe)}" >/dev/null 2>&1 &
"""
        # pkill -x (exact process NAME), never -f: -f matches the whole command line,
        # so it would kill any unrelated process that merely mentions poke_updater.
        script = f"""#!/bin/sh
sleep 3
pkill -x poke_updater >/dev/null 2>&1
{copy_updater}
rm -rf "{temp_path}"
{launch_game}
sleep 1
rm -f "$0"
"""
        script_path = os.path.join(path_to_use, 'cleanup.sh')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        command = ['/bin/sh', script_path]
        kwargs = {'start_new_session': True}  # survive this process exiting

    subprocess.Popen(command, **kwargs)
    sleep(0.5)  # let the script start before we release our file locks
    # os._exit and not sys.exit: this runs on the worker thread, where sys.exit only
    # raises SystemExit in that thread and leaves the process (and its file locks)
    # alive. The cleanup script needs us gone to replace the updater's own files.
    logging.shutdown()
    os._exit(0)

def delete_old_files(ignored_folders):
    """Delete the installed game, keeping the ignored folders (user data), the
    updater itself and the temp folder holding the new version.

    Returns False if the user cancelled mid-way.
    """
    for root, folders, files in os.walk(path_to_use):
        if cancelled():
            return False
        for folder in folders:
            folder_path = os.path.join(root, folder)
            if folder.startswith(".") or folder == TEMP_PATH or "poke_updater" in folder:
                continue
            if should_ignore_folder(folder, folder_path, ignored_folders):
                continue
            shutil.rmtree(folder_path, ignore_errors=True)
        # Whatever survives here is deliberately kept, so never descend into it
        folders[:] = []
        for file in files:
            if file.startswith(".") and file != ".nomedia":
                continue
            if file == LOG_FILE:  # open handle: Windows refuses to delete it
                continue
            os.remove(os.path.join(root, file))
    return True

def read_settings(settings_path):
    """Read the KEY=VALUE lines of pu_config into a dict."""
    settings = {}
    with open(settings_path, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", maxsplit=1)
            settings[key.strip()] = value.strip().replace('"', '')
    return settings

def version_tuple(version):
    """1.2.3 -> (1, 2, 3). Non-numeric parts (1.2b) are ignored rather than fatal."""
    return tuple(int(part) for part in re.findall(r'\d+', version))

def compare_versions(new_version, current_version):
    return version_tuple(new_version) > version_tuple(current_version)

def main():
    global current_step, download
    poke_updater_from_zip = None
    download = Download(app, path_to_use, TEMP_PATH, LANGUAGE)
    try: 
        # Retrieve game version and download link from settings file
        current_step = Step.RETRIEVING
        app.set_step(Step.RETRIEVING[1][LANGUAGE])
        settings_path = os.path.join(path_to_use, SETTINGS_FILE)
        
        settings = read_settings(settings_path)

        downloaded_version = settings.get("CURRENT_GAME_VERSION")
        # PASTEBIN_URL is the current key; VERSION_PASTEBIN is what older configs
        # (and the Ruby plugin) still write.
        pastebin_url = settings.get("PASTEBIN_URL") or settings.get("VERSION_PASTEBIN")
        folders_str = settings.get("IGNORED_FOLDERS", "")
        ignored_folders = [f.strip() for f in folders_str.split(",") if f.strip()] or ["Fotos"]

        if not pastebin_url:
            app.show_error(ExceptionMessage.NO_PASTEBIN_URL[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        if not 'raw' in pastebin_url:
            app.show_error(ExceptionMessage.PASTEBIN_NOT_RAW_URL[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        try:
            response = requests.get(pastebin_url, timeout=15)
            if response.status_code != 200:
                app.show_error(ExceptionMessage.NO_PASTEBIN_CONTENT[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
            new_version = None
            for line in response.text.split("\n"):
                line = line.strip()
                if "GAME_VERSION" in line and not new_version and "=" in line:
                    new_version = line.split("=")[1].strip()
                elif "DOWNLOAD_URL" in line and "=" in line:
                    game_url = line.split("=", maxsplit=1)[1].strip()
                    try:
                        host = download.get_file_host(game_url)
                    except Exception:
                        logging.warning("Unsupported download host: %s", game_url)
                        continue
                    download_hosts[HostNames.get_name(host)] = game_url
            if not download_hosts:
                app.show_error(ExceptionMessage.NO_VALID_FILE_HOST[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
            if not new_version or not version_tuple(new_version):
                app.show_error(ExceptionMessage.INVALID_VERSION_NUMBER[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
            if not downloaded_version or not compare_versions(new_version, downloaded_version):
                app.show_info(ExceptionMessage.NO_NEW_VERSION[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                app.bring_to_front()  # Bring window to front to show the "no update" message
                return
        except requests.ConnectionError:
            app.show_error(ExceptionMessage.NO_INTERNET[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        # Download new version
        if os.path.exists(os.path.join(path_to_use, TEMP_PATH)):
            shutil.rmtree(os.path.join(path_to_use, TEMP_PATH))
        current_step = Step.DOWNLOADING
        app.set_step(Step.DOWNLOADING[1][LANGUAGE])
        app.start_progress(indeterminate=False)

        if not os.path.exists(os.path.join(path_to_use, TEMP_PATH)):
            os.mkdir(os.path.join(path_to_use, TEMP_PATH))
        try:
            if len(download_hosts.keys()) > 1:
                game_url = app.choose_download_host()
            else:
                game_url = list(download_hosts.values())[0]

            download.start_download(game_url)
            if kill.is_set(): return
        except ConnectionResetError:
            app.show_error(ExceptionMessage.DOWNLOAD_ERROR[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        except BandwithExceededError:
            app.show_error(ExceptionMessage.BANDWIDTH_EXCEEDED[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        except Exception:
            logging.exception("Download failed")
            app.show_error(ExceptionMessage.DOWNLOAD_ERROR[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        app.set_note("")

        # Extract files
        current_step = Step.EXTRACTING
        app.set_step(Step.EXTRACTING[1][LANGUAGE])
        app.set_note(ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        app.start_progress()
        found_file = False
        # Redirect stdout and stderr if they are None (happens with WIN32GUI)
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()
        for file in os.listdir(os.path.join(path_to_use, TEMP_PATH)):
            file_suffix = pathlib.Path(file).suffix
            if file_suffix in [".zip", ".rar", ".7z", ".tar.gz"]:
                found_file = True
                file_to_extract = os.path.join(path_to_use, TEMP_PATH, file)
                break
        
        if not found_file:
            app.show_error(ExceptionMessage.NO_VALID_FILE_FOUND[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        
        not_extracting.clear()
        outdir = os.path.join(path_to_use, TEMP_PATH)
        try:
            if file_suffix == ".zip":
                try:
                    with zipfile.ZipFile(file_to_extract, 'r') as zip_ref:
                        zip_ref.extractall(outdir)
                except zipfile.BadZipFile:
                    app.show_error(ExceptionMessage.INVALID_ZIP_FILE[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                    return
                except Exception as e:
                    logging.exception("Extraction failed")
                    app.show_error(ExceptionMessage.UNEXPECTED_ERROR[LANGUAGE], e)
                    return
            else:
                extract_archive(file_to_extract, outdir=outdir)
        finally:
            not_extracting.set()

        if cancelled(): return

        os.remove(file_to_extract)
        app.set_note("")
        app.stop_progress()

        # Nothing may be deleted until the new game is known to be intact: the
        # delete step is not reversible.
        extracted_path = os.path.join(path_to_use, TEMP_PATH)
        if not find_game_exe_recursive(extracted_path):
            app.show_error(ExceptionMessage.NO_VALID_FOLDER_FOUND[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        # Delete old files
        current_step = Step.DELETING
        app.set_step(Step.DELETING[1][LANGUAGE])
        app.set_note(ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        app.start_progress()
        if not delete_old_files(ignored_folders):
            return
        app.stop_progress()

        # Move files
        current_step = Step.MOVING
        app.set_step(Step.MOVING[1][LANGUAGE])
        app.set_note(ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        app.start_progress()

        # Use the new complex directory structure handler
        success, poke_updater_from_zip = handle_complex_directory_structure(extracted_path, path_to_use, ignored_folders)

        if not success:
            app.show_error(ExceptionMessage.NO_VALID_FOLDER_FOUND[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        # Zip archives carry no permission bits, so the Linux binary lands without +x
        if not IS_WINDOWS:
            make_game_executable(path_to_use)

        app.stop_progress()
        app.set_note("")

        # Post update
        app.set_note("")
        app.start_progress(indeterminate=False)
        app.set_step(ProgressLabel.DONE[LANGUAGE])
        sleep(1)
        app.set_progress(1)


        # Play completion chime and bring window to front
        app.play_completion_chime()
        app.bring_to_front()
        
        sleep(2)

        if getattr(sys, 'frozen', False) or test:
            remove_updater(poke_updater_from_zip)  # never returns: it kills the process

        # Not frozen (development run): close the window from the main thread and let
        # this worker end by returning. Calling app.quit() here would touch Tk from
        # the wrong thread, and sys.exit() would only raise inside the worker.
        app.ui(app.quit)
        return
    except Exception as e:
        logging.exception("Update failed at step %s", current_step)
        app.show_error(ExceptionMessage.UNEXPECTED_ERROR[LANGUAGE], e)
        return

customtkinter.set_default_color_theme("dark-blue")

class Dialog(customtkinter.CTkToplevel):
    """Themed replacement for tkinter.messagebox, whose native X11 widgets look
    nothing like the rest of the app. Modal: blocks until the player answers."""
    WARNING_COLOR = '#e0a030'

    def __init__(self, parent, title, message, confirm=False, warning=False):
        super().__init__(parent)
        self.result = False
        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        frame = customtkinter.CTkFrame(self, fg_color="transparent")
        frame.pack(padx=25, pady=20, fill="both", expand=True)

        if warning:
            customtkinter.CTkLabel(frame, text="⚠", font=("", 34),
                                   text_color=Dialog.WARNING_COLOR).pack(pady=(0, 8))

        customtkinter.CTkLabel(frame, text=message, wraplength=360,
                               justify="left").pack(pady=(0, 18))

        buttons = customtkinter.CTkFrame(frame, fg_color="transparent")
        buttons.pack()
        if confirm:
            customtkinter.CTkButton(buttons, text=QuitBoxTitle.OPTIONS['NO'][LANGUAGE], width=110,
                                    fg_color="transparent", border_width=1,
                                    command=self.on_cancel).pack(side="left", padx=6)
        confirm_text = QuitBoxTitle.OPTIONS['YES'][LANGUAGE] if confirm else "OK"
        ok = customtkinter.CTkButton(buttons, text=confirm_text, width=110, command=self.on_ok)
        ok.pack(side="left", padx=6)

        self.center_on(parent)
        self.bind("<Return>", lambda _event: self.on_ok())
        self.bind("<Escape>", lambda _event: self.on_cancel())
        ok.focus_set()
        self.transient(parent)
        # X11 refuses a grab on a window that is not mapped yet ("grab failed: window
        # not viewable"), unlike Windows. Wait for it to be on screen first.
        self.wait_visibility()
        self.grab_set()          # modal: swallow clicks on the main window
        self.wait_window()       # block the caller until this window closes

    def center_on(self, parent):
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def on_ok(self):
        self.result = True
        self.destroy()

    def on_cancel(self):
        self.result = False
        self.destroy()

def ask_ok_cancel(title, message):
    return Dialog(app, title, message, confirm=True, warning=True).result

def show_dialog(title, message):
    Dialog(app, title, message).result

class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.focus()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.geometry("300x200")
        self.resizable(False, False)

        self.label = customtkinter.CTkLabel(self, text="Elija el host para la descarga")
        self.label.pack(padx=10, pady=10)
        self.combobox = customtkinter.CTkComboBox(self, values=list(download_hosts.keys()), state="readonly")
        self.combobox.set(list(download_hosts.keys())[0])
        self.combobox.pack(padx=10, pady=10)

        self.button = customtkinter.CTkButton(self, text="OK", command=self.on_ok)
        self.button.pack(padx=10, pady=10)

    def on_ok(self):
        host = self.combobox.get()
        url = download_hosts[host]
        app.set_download_host(url)
        self.destroy()
    
    def on_closing(self):
        # self.destroy()
        app.on_closing()

class App(customtkinter.CTk):
    ERROR_COLOR = '#cc3030'
    def __init__(self):
        super().__init__()
        self.title("Pokemon Essentials Game Updater")
        self.resizable(False, False)
        self.progressbar = None
        self.columnconfigure(0, weight=1)
        self.set_icon()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()
        self.download_host = None
        self.host_chosen = threading.Event()
        self.second_window = None
        # Tk is not thread-safe: the worker hands widget updates to the main
        # loop through this queue instead of touching widgets itself.
        self.ui_queue = queue.SimpleQueue()
        self.pump_ui_queue()

    def resource(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
        return os.path.join(base_path, relative_path)

    def set_icon(self):
        try:
            if IS_WINDOWS:
                self.iconbitmap(self.resource("poke_updater_logo.ico"))
            else:
                # .ico is a Windows-only format for Tk; X11 needs a PhotoImage
                self.iconphoto(True, tk.PhotoImage(file=self.resource("poke_updater_logo.png")))
        except Exception:
            logging.warning("Could not set the window icon", exc_info=True)

    # --- thread-safe UI ---
    def ui(self, fn, *args, **kwargs):
        """Queue a widget update to run on the Tk main thread."""
        self.ui_queue.put((fn, args, kwargs))

    def pump_ui_queue(self):
        while True:
            try:
                fn, args, kwargs = self.ui_queue.get_nowait()
            except queue.Empty:
                break
            try:
                fn(*args, **kwargs)
            except Exception:
                logging.exception("UI update failed")
        self.after(50, self.pump_ui_queue)

    def set_step(self, text):
        self.ui(self.step_label.configure, text=text)

    def set_note(self, text):
        self.ui(self.progress_label.configure, text=text)

    def set_progress(self, fraction):
        self.ui(self.progressbar.set, fraction)

    def start_progress(self, indeterminate=True):
        self.ui(self.progressbar.configure, mode="indeterminate" if indeterminate else "determinate")
        self.ui(self.progressbar.set, 0)
        if indeterminate:
            self.ui(self.progressbar.start)

    def stop_progress(self):
        self.ui(self.progressbar.stop)

    def create_widgets(self):
        self.label = customtkinter.CTkLabel(self, text=ExceptionMessage.DO_NOT_CLOSE[LANGUAGE])
        self.label.grid(row=0, column=0, pady=5, padx=15, sticky='w')

        self.step_label = customtkinter.CTkLabel(self, text="")
        self.step_label.grid(row=1, column=0, pady=5, padx=15, sticky='w')

        self.progress_label = customtkinter.CTkLabel(self, text="")
        self.progress_label.grid(row=1, column=0, pady=5, padx=15, sticky='e')

        self.progressbar = customtkinter.CTkProgressBar(self, orientation="horizontal")
        self.progressbar.grid(row=2, column=0, pady=10, padx=15, sticky=tk.E+tk.W)
    
    def set_download_host(self, host):
        self.download_host = host
        self.host_chosen.set()

    def choose_download_host(self):
        """Called from the worker thread: open the picker and block until the
        player answers."""
        self.ui(self.open_host_window)
        self.host_chosen.wait()
        self.ui(self.deiconify)
        return self.download_host

    def open_host_window(self):
        self.second_window = ToplevelWindow(self)
        self.second_window.focus()
        self.withdraw()

    def show_error(self, step_text, label_text):
        logging.error("%s: %s", step_text, label_text)
        self.ui(self.step_label.configure, text=step_text, text_color=App.ERROR_COLOR)
        self.ui(self.label.configure, text=label_text, text_color=App.ERROR_COLOR)

    def show_info(self, step_text, label_text):
        self.ui(self.step_label.configure, text=step_text)
        self.ui(self.label.configure, text=label_text)

    def play_completion_chime(self):
        """Play a chime when the update completes."""
        sound_path = self.resource("GUI save game.ogg")
        try:
            if IS_WINDOWS:
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                # No stdlib audio on Linux; use whatever player the desktop has,
                # and fall back to the terminal bell.
                for player in ("paplay", "pw-play", "ffplay"):  # aplay can't read .ogg
                    if shutil.which(player):
                        args = [player, "-nodisp", "-autoexit", sound_path] if player == "ffplay" else [player, sound_path]
                        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return
                self.ui(self.bell)
        except Exception:
            logging.warning("Could not play the completion chime", exc_info=True)


    def bring_to_front(self):
        """Bring the window to front and focus it if minimized. Safe to call
        from the worker thread."""
        self.ui(self._bring_to_front)

    def _bring_to_front(self):
        try:
            if self.state() == 'iconic':
                self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.after(100, lambda: self.attributes('-topmost', False))
            self.focus_force()
        except Exception:
            logging.warning("Failed to bring window to front", exc_info=True)
            try:
                self.lift()
            except Exception:
                pass


    def on_closing(self):
        resume.clear()
        if download:
            download.set_wait(True)
        if ask_ok_cancel(QuitBoxTitle.TITLE[LANGUAGE], Reversal.getMessageText(current_step, LANGUAGE)):
            if self.second_window:
                self.second_window.destroy()
            if not not_extracting.is_set():
                show_dialog(Reversal.REVERSAL_TEXT[3][LANGUAGE][0], Reversal.REVERSAL_TEXT[3][LANGUAGE][1])
                # Extraction can't be interrupted safely, so block (without spinning)
                # until it finishes, then reverse it.
                not_extracting.wait()
            kill.set()
            resume.set()  # release the worker so it can see the kill and return
            if download:
                download.set_kill(True)
            Reversal.reverse(current_step, os.path.join(path_to_use, TEMP_PATH))
            app.destroy()
        else:
            resume.set()
            if download:
                download.set_wait(False)


if __name__ == "__main__":
    app = App()
    thread = threading.Thread(target=main, daemon=True)
    thread.start()
    app.mainloop()
