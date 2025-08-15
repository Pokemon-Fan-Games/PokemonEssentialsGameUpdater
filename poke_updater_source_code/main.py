import os
from time import sleep
import sys
import io
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import shutil
import pathlib
import ctypes
from locales import *
from download import *
from exceptions import *
import locale
from download import Download
from subprocess import Popen, DETACHED_PROCESS, PIPE
from patoolib import extract_archive
import zipfile
from reversal import Reversal
from worker import create_worker
import customtkinter
import subprocess

wait = False
kill = False
is_extracting = False

download_hosts = {}
# Determine if application is a script file or exe
if getattr(sys, 'frozen', False):
    REAL_PATH = os.path.dirname(os.path.dirname(sys.executable))
elif __file__:
    REAL_PATH = os.path.dirname(__file__)

TEST_PATH = os.path.join('C:', os.sep, 'Users', 'Diego', 'Downloads')
test = False
path_to_use = TEST_PATH if test else REAL_PATH

# Get user language for messages
user_locale = locale.windows_locale[ ctypes.windll.kernel32.GetUserDefaultUILanguage() ].lower()
LANGUAGE = user_locale.split("_")[0] if '_' in user_locale else user_locale

SETTINGS_FILE = "pu_config"
TEMP_PATH = "temp"
current_step = None
download = None

def find_game_exe_recursive(root_path):
    """
    Recursively search for Game.exe in the directory structure.
    Returns the directory containing Game.exe, or None if not found.
    """
    for root, dirs, files in os.walk(root_path):
        if "Game.exe" in files:
            return root
    return None

def copy_directory_contents_recursively(src_root, dst_root, src_base_path, exclude_paths=None):
    """
    Recursively copy contents from src_root to dst_root, maintaining directory structure.
    
    Args:
        src_root: Source directory to copy from
        dst_root: Destination directory to copy to
        src_base_path: Base path used to calculate relative paths
        exclude_paths: Set of paths to exclude from copying
    """
    if exclude_paths is None:
        exclude_paths = set()
    
    for root, dirs, files in os.walk(src_root):
        # Calculate relative path from the base source path
        rel_path = os.path.relpath(root, src_base_path)
        
        # Skip if this path should be excluded
        if root in exclude_paths:
            continue
        
        # Create destination directory if it doesn't exist
        if rel_path != '.':
            dst_dir = os.path.join(dst_root, rel_path)
            os.makedirs(dst_dir, exist_ok=True)
        else:
            dst_dir = dst_root
        
        # Copy files
        for file in files:
            if file.startswith(".") and file != ".nomedia":
                continue
            if "poke_updater" in file:
                continue
            if '.git' in file:
                continue
                
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_dir, file)
            
            # Remove destination file if it exists
            if os.path.exists(dst_file):
                os.remove(dst_file)
            
            shutil.move(src_file, dst_file)

def handle_complex_directory_structure(extracted_path, destination_path):
    """
    Handle complex directory structures where Game.exe might be nested.
    Accounts for the fact that the updater runs from inside the game directory.
    """
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
                        
                        src_file = os.path.join(root, file)
                        
                        # Handle poke_updater files specially
                        if "poke_updater" in file:
                            poke_updater_from_zip = src_file
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
                
                # Remove destination directory if it exists
                if os.path.exists(dst_item):
                    shutil.rmtree(dst_item)
                
                # Move the directory
                shutil.move(src_item, dst_item)
        
        elif os.path.isfile(src_item):
            # Handle individual files at root level
            if "poke_updater" in item:
                poke_updater_from_zip = src_item
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
    # Define the flag for hiding the window
    CREATE_NO_WINDOW = 0x08000000
    ROBOCOPY_PARAMS = "/e /dcopy:da /ns /nc /nfl /ndl /np /njh /njs"
    if not poke_updater_from_zip: 
        command = f'ping localhost -n 2 & rmdir /s /q "{os.path.join(path_to_use, TEMP_PATH)}"'
        Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    else:
        # Get the absolute paths for the batch file
        game_exe_path = os.path.join(path_to_use, 'Game.exe')
        poke_updater_dir = os.path.join(path_to_use, 'poke_updater')
        temp_path = os.path.join(path_to_use, TEMP_PATH)
        
        # Get the directory where the current executable is located
        # This should be deleted after copying the new updater
        if getattr(sys, 'frozen', False):
            # Running as executable
            current_updater_dir = os.path.dirname(os.path.realpath(sys.executable))
        else:
            # Running as script (for development)
            current_updater_dir = os.path.dirname(os.path.realpath(__file__))
        
        batch_commands = f"""@echo off
timeout /t 5
taskkill /f /im poke_updater.exe 2>nul 
rmdir /s /q "{current_updater_dir}"
start "" "{game_exe_path}"
robocopy "{poke_updater_from_zip}" "{poke_updater_dir}" {ROBOCOPY_PARAMS}
rmdir /s /q "{temp_path}"
DEL "%~f0"
"""
        batch_file_path = os.path.join(path_to_use, 'cleanup.bat')

        # Write the batch file
        with open(batch_file_path, 'w') as batch_file:
            batch_file.write(batch_commands)
        
        # Start the cleanup batch file
        subprocess.Popen(['cmd.exe', '/c', batch_file_path], creationflags=CREATE_NO_WINDOW)
        
        # Give the batch file a moment to start
        sleep(0.5)
        
        # Exit cleanly to release file locks as soon as possible
        sys.exit(0)

def compare_versions(new_version, current_version):
    # Split version strings into tuples of integers
    old_version_nums = tuple(map(int, current_version.split('.')))
    new_version_nums = tuple(map(int, new_version.split('.')))
    
    # Compare version numbers directly
    return new_version_nums > old_version_nums

def main():
    global current_step, is_extracting, download
    poke_updater_from_zip = None
    download = Download(app, path_to_use, TEMP_PATH, LANGUAGE)
    try: 
        # Retrieve game version and download link from settings file
        current_step = Step.RETRIEVING
        app.step_label.configure(text=Step.RETRIEVING[1][LANGUAGE])
        settings_path = os.path.join(path_to_use, SETTINGS_FILE)
        with open(settings_path, encoding='utf-8') as file:
            downloaded_version = None
            pastebin_url = None
            while line := file.readline():
                if "CURRENT_GAME_VERSION" in line:
                    downloaded_version = line.split("=")[1].strip()
                if "PASTEBIN_URL" in line:
                    pastebin_url = line.split("=")[1].strip().replace('"', '')
                if downloaded_version and pastebin_url:
                    break 

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
            game_url = None
            lines = response.text.split("\n")
            for line in lines:
                line = line.strip()
                if "GAME_VERSION" in line and not new_version:
                    split_line = line.split("=")
                    if len(split_line) > 1:
                        try:
                            new_version = split_line[1].strip()
                        except ValueError:
                            app.show_error(ExceptionMessage.INVALID_VERSION_NUMBER[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                            return
                    new_version = line.split("=")[1].strip()
                elif "DOWNLOAD_URL" in line:
                    game_url = line.split("=", maxsplit=1)[1].strip()
                    try:
                        host = download.get_file_host(game_url)
                    except Exception:
                        continue
                    host_name = HostNames.get_name(host)
                    download_hosts[host_name] = game_url
            if not download_hosts:
                app.show_error(ExceptionMessage.NO_VALID_FILE_HOST[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
            if not downloaded_version or not compare_versions(new_version, downloaded_version):
                app.show_info(ExceptionMessage.NO_NEW_VERSION[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
        except requests.ConnectionError:
            app.show_error(ExceptionMessage.NO_INTERNET[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        # Download new version
        if os.path.exists(os.path.join(path_to_use, TEMP_PATH)):
            shutil.rmtree(os.path.join(path_to_use, TEMP_PATH))
        current_step = Step.DOWNLOADING
        app.step_label.configure(text=Step.DOWNLOADING[1][LANGUAGE])
        app.progressbar.set(0)

        if not os.path.exists(os.path.join(path_to_use, TEMP_PATH)):
            os.mkdir(os.path.join(path_to_use, TEMP_PATH))
        try:
            if len(download_hosts.keys()) > 1:
                game_url = app.choose_download_host()
            else:
                game_url = list(download_hosts.values())[0]

            download.start_download(game_url)
            if kill: return
        except ConnectionResetError:
            app.show_error(ExceptionMessage.DOWNLOAD_ERROR[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        except BandwithExceededError:
            app.show_error(ExceptionMessage.BANDWIDTH_EXCEEDED[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        except Exception as e:
            print(e)
            app.show_error(ExceptionMessage.DOWNLOAD_ERROR[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        app.progress_label.configure(text="")

        # Extract files
        current_step = Step.EXTRACTING
        app.step_label.configure(text=Step.EXTRACTING[1][LANGUAGE])
        app.progressbar.configure(mode="indeterminate")
        app.progressbar.set(0)
        app.progress_label.configure(text=ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        app.progressbar.start()
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
        
        is_extracting = True
        outdir = os.path.join(path_to_use, TEMP_PATH)
        if file_suffix == ".zip":
            try:
                with zipfile.ZipFile(file_to_extract, 'r') as zip_ref:
                    zip_ref.extractall(outdir)
            except zipfile.BadZipFile:
                app.show_error(ExceptionMessage.INVALID_ZIP_FILE[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
            except Exception as e:
                print(e)
                app.show_error(ExceptionMessage.UNEXPECTED_ERROR[LANGUAGE], e)
        else:
            extract_archive(file_to_extract, outdir=outdir)
        
        is_extracting = False
        while wait:
            if kill: return



        os.remove(file_to_extract)
        app.progress_label.configure(text="")
        app.progressbar.stop()
        app.progressbar.set(0)
        app.progressbar.configure(mode="indeterminate")

        # Delete old files
        current_step = Step.DELETING
        app.step_label.configure(text=Step.DELETING[1][LANGUAGE])
        app.progress_label.configure(text=ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        app.progressbar.set(0)
        app.progressbar.start()
        for root, folders, files in os.walk(path_to_use):
            while wait:
                if kill: return
            if 'poke_updater' in root or TEMP_PATH in root: continue
            for folder in folders:
                if folder.startswith(".") or folder == TEMP_PATH or "poke_updater" in folder: continue
                shutil.rmtree(os.path.join(root, folder))
            for file in files:
                if (file.startswith(".") and file != ".nomedia") or file == TEMP_PATH: continue
                file_to_remove = os.path.join(path_to_use,file)
                os.remove(file_to_remove)
        app.progressbar.stop()

        # Move files
        current_step = Step.MOVING
        app.step_label.configure(text=Step.MOVING[1][LANGUAGE])
        app.progressbar.set(0)
        app.progressbar.configure(mode="interminate")
        app.progress_label.configure(text="")
        

        extracted_path = os.path.join(path_to_use, TEMP_PATH)
        app.progress_label.configure(text=ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        app.progressbar.start()
        
        # Use the new complex directory structure handler
        success, poke_updater_from_zip = handle_complex_directory_structure(extracted_path, path_to_use)
        
        if not success:
            app.show_error(ExceptionMessage.NO_VALID_FOLDER_FOUND[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return
        
        app.progressbar.stop()
        app.progress_label.configure(text="")

        # Post update
        app.progress_label.configure(text="")
        app.progressbar.configure(mode="determinate")
        app.step_label.configure(text=f'{ProgressLabel.DONE[LANGUAGE]} {ProgressLabel.LAUNCH[LANGUAGE]} {ProgressLabel.A_FEW_SECONDS_SHORT[LANGUAGE]}')
        sleep(1)
        app.progressbar.set(1)
        sleep(1)

        if getattr(sys, 'frozen', False) or test:
            remove_updater(poke_updater_from_zip)

        app.main_thread.stop()
        app.quit()
        sys.exit()
    except Exception as e: 
        print(e)
        app.show_error(ExceptionMessage.UNEXPECTED_ERROR[LANGUAGE], e)
        return

customtkinter.set_default_color_theme("dark-blue")
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
        self.iconbitmap(self.resource("poke_updater_logo.ico"))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_widgets()
        self.download_host = None
        self.second_window = None
        self.main_thread = None
    def resource(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
        return os.path.join(base_path, relative_path)
    
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
    
    def choose_download_host(self):
        self.second_window = ToplevelWindow(self)
        self.second_window.focus()
        self.withdraw()
        while not self.download_host:
            sleep(0.1)
        self.deiconify()
        return self.download_host
    def show_error(self, step_text, label_text):
        self.step_label.configure(text=step_text, text_color=App.ERROR_COLOR)
        self.label.configure(text=label_text, text_color=App.ERROR_COLOR)

    def show_info(self, step_text, label_text):
        self.step_label.configure(text=step_text)
        self.label.configure(text=label_text)
    
    def on_closing(self):
        global wait, kill, is_extracting, download
        wait = True
        if download:
            download.set_wait(True)
        self.main_thread.pause()
        if messagebox.askokcancel(QuitBoxTitle.TITLE[LANGUAGE], Reversal.getMessageText(current_step, LANGUAGE), icon=messagebox.WARNING):
            if self.second_window:
                self.second_window.destroy()
            if is_extracting:
                messagebox.showinfo(Reversal.REVERSAL_TEXT[3][LANGUAGE][0], Reversal.REVERSAL_TEXT[3][LANGUAGE][1])
            while is_extracting:
                pass  # Freeze app after showing a message while files are extracting to be able to reverse
            # self.main_thread.resume()
            kill = True
            if download:
                download.set_kill(True)
            self.main_thread.stop()
            Reversal.reverse(current_step, os.path.join(path_to_use, TEMP_PATH))
            app.destroy()
        else:
            wait = False
            self.main_thread.resume()


if __name__ == "__main__":
    app = App()
    thread = create_worker(main, daemon=True) 
    app.main_thread = thread
    app.mainloop()
