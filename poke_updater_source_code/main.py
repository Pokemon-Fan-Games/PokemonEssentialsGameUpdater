# -*- coding: utf-8 -*-
import os
from time import sleep
import sys
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import shutil
import pathlib
import ctypes
from locales import *
from download import *
import locale
from download import Download
from subprocess import Popen, DETACHED_PROCESS, PIPE
from patoolib import extract_archive
from reversal import Reversal
from worker import create_worker
import customtkinter
import darkdetect

wait = False
kill = False
is_extracting = False

download_hosts = {}
# Determine if application is a script file or exe
if getattr(sys, 'frozen', False):
    REAL_PATH = os.path.dirname(os.path.dirname(sys.executable))
elif __file__:
    REAL_PATH = os.path.dirname(__file__)

TEST_PATH = r""
test = False
path_to_use = TEST_PATH if test else REAL_PATH

# Get user language for messages
user_locale = locale.windows_locale[ ctypes.windll.kernel32.GetUserDefaultUILanguage() ].lower()
LANGUAGE = user_locale.split("_")[0] if '_' in user_locale else user_locale

SETTINGS_FILE = "pu_config"
TEMP_PATH = "temp"
current_step = None
download = None

def remove_updater(poke_updater_from_zip):
    if not poke_updater_from_zip: 
        command = f'ping localhost -n 2 & rmdir /s /q "{os.path.join(path_to_use, TEMP_PATH)}"'
    else:
        command = f'ping localhost -n 5 & rmdir /s /q "{os.path.dirname(os.path.realpath(sys.executable))}" ' \
                f'& move "{poke_updater_from_zip}" "{path_to_use}" ' \
                f'& rmdir /s /q "{os.path.join(path_to_use, TEMP_PATH)}"'
    Popen(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, shell=True)

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
                if "VERSION_PASTEBIN" in line:
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
                # if new_version and game_url:
                #     break
                if "GAME_VERSION" in line and not new_version:
                    split_line = line.split("=")
                    if len(split_line) > 1:
                        try:
                            new_version = float(split_line[1].strip())
                        except ValueError:
                            app.show_error(ExceptionMessage.INVALID_VERSION_NUMBER[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                            return
                    new_version = float(line.split("=")[1].strip())
                elif "DOWNLOAD_URL" in line:
                    game_url = line.split("=", maxsplit=1)[1].strip()
                    try:
                        host = download.get_file_host(game_url)
                    except Exception:
                        continue
                    host_name = HostNames.get_name(host)
                    download_hosts[host_name] = game_url
            # newVersion = float(response.text.split("\n")[0].strip().split("=")[1].strip())
            if not download_hosts:
                app.show_error(ExceptionMessage.NO_VALID_FILE_HOST[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
                return
            if not downloaded_version or new_version <= float(downloaded_version):
                app.show_error(ExceptionMessage.NO_NEW_VERSION[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
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
        # game_url = response.text.split("\n")[1].strip().split("=", maxsplit=1)[1].strip()

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
        for file in os.listdir(os.path.join(path_to_use, TEMP_PATH)):
            file_suffix = pathlib.Path(file).suffix
            if file_suffix in [".zip", ".rar", ".7z", ".tar.gz"]:
                found_file = True
                file_to_extract = os.path.join(path_to_use, TEMP_PATH, file)
                is_extracting = True
                outdir = os.path.join(path_to_use, TEMP_PATH)
                extract_archive(file_to_extract, outdir=outdir)
                break
        
        is_extracting = False
        while wait:
            if kill: return

        if not found_file:
            app.show_error(ExceptionMessage.NO_VALID_FILE_FOUND[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        os.remove(file_to_extract)
        app.progress_label.configure(text="")
        app.progressbar.stop()

        # Delete old files
        current_step = Step.DELETING
        app.step_label.configure(text=Step.DELETING[1][LANGUAGE])
        app.progress_label.configure(text=ProgressLabel.A_FEW_SECONDS[LANGUAGE])
        items_to_remove = os.listdir(path_to_use)
        items_to_ignore = []
        total_files = 0
        for root, _,  files in os.walk(path_to_use):
            if 'poke_updater' in root:
                for file in files:
                    items_to_ignore.append(file)
            total_files+= len(files)
        #total_files = sum([len(files) for _, _, files in os.walk(path_to_use)])
        deleted_items = 0
        for file in items_to_remove:
            while wait:
                if kill: return
            if file.startswith(".") or file == TEMP_PATH: continue
            app.progressbar.set(deleted_items/total_files)
            app.progress_label.configure(text=str(round(app.progressbar.get() * 100)) + "%")
            if "poke_updater" not in file and file not in items_to_ignore:
                file_to_remove = os.path.join(path_to_use,file)
                if os.path.isdir(file_to_remove):
                    deleted_tree_count = sum([len(files) for _, _, files in os.walk(os.path.join(path_to_use, file_to_remove))])
                    shutil.rmtree(file_to_remove)
                    deleted_items += deleted_tree_count
                else:
                    os.remove(file_to_remove)
                    deleted_items += 1
        app.progress_label.configure(text="")

        # Move files
        current_step = Step.MOVING
        app.step_label.configure(text=Step.MOVING[1][LANGUAGE])
        app.progressbar.configure(mode="determinate")
        app.progressbar.set(0)
        app.progress_label.configure(text=ProgressLabel.UNKNOWN_TIME[LANGUAGE])

        extracted_path = os.path.join(path_to_use, TEMP_PATH)
        for file in os.listdir(extracted_path):
            while wait:
                if kill: return
            if os.path.isdir(os.path.join(extracted_path, file)) and not file.startswith("."):
                extracted_folder = os.path.join(extracted_path, file)
                break
        
        if not extracted_folder:
            app.show_error(ExceptionMessage.NO_VALID_FOLDER_FOUND[LANGUAGE], ExceptionMessage.CLOSE_WINDOW[LANGUAGE])
            return

        total_files = sum([len(files) for _, _, files in os.walk(extracted_folder)])
        moved_files = 0
        for file in os.listdir(extracted_folder):
            while wait:
                if kill: return
            app.progressbar.set(moved_files/total_files)
            app.progress_label.configure(text=str(round(app.progressbar.get() * 100)) + "%")
            if "poke_updater" in file and os.path.isdir(file):
                file_tree_count = sum([len(files) for _, _, files in os.walk(os.path.join(path_to_use, extracted_folder, file))])
                moved_files += file_tree_count
                poke_updater_from_zip = os.path.join(extracted_folder, file)
            elif os.path.join(path_to_use, file) != os.path.join(path_to_use, TEMP_PATH):
                if os.path.isdir(os.path.join(extracted_folder, file)):
                    file_tree_count = sum([len(files) for _, _, files in os.walk(os.path.join(path_to_use, extracted_folder, file))])
                    moved_files += file_tree_count
                else:
                    moved_files += 1
                shutil.move(os.path.join(extracted_folder, file), path_to_use)
            else:
                file_tree_count = sum([len(files) for _, _, files in os.walk(os.path.join(path_to_use, extracted_folder, file))])
                moved_files += file_tree_count
        app.progress_label.configure(text="")

        # Post update
        for i in range(5):
            app.step_label.configure(text=f'{ProgressLabel.DONE[LANGUAGE]} {str(5-i)} {ProgressLabel.SECONDS[LANGUAGE]}')
            sleep(1)
        
        Popen(os.path.join(path_to_use,"Game.exe"), stdin=PIPE, stderr=PIPE, stdout=PIPE, creationflags=DETACHED_PROCESS)
        if getattr(sys, 'frozen', False):
            remove_updater(poke_updater_from_zip)

        app.quit()
        app.main_thread.stop()
    except Exception as e: 
        print(e)
        app.show_error(ExceptionMessage.UNEXPECTED_ERROR[LANGUAGE], e)
        return

customtkinter.set_default_color_theme("dark-blue")
class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.focus()
        self.geometry("300x200")
        self.resizable(False, False)

        self.label = customtkinter.CTkLabel(self, text="Elija el host para la descarga")
        self.label.pack(padx=10, pady=10)
        self.combobox = customtkinter.CTkComboBox(self, values=list(download_hosts.keys()))
        self.combobox.pack(padx=10, pady=10)

        self.button = customtkinter.CTkButton(self, text="OK", command=self.on_ok)
        self.button.pack(padx=10, pady=10)

    def on_ok(self):
        host = self.combobox.get()
        url = download_hosts[host]
        app.set_download_host(url)
        self.destroy()

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
    
    def on_closing(self):
        global wait, kill, is_extracting, download
        wait = True
        download.set_wait(True)
        self.main_thread.pause()
        if messagebox.askokcancel(QuitBoxTitle.TITLE[LANGUAGE], Reversal.getMessageText(current_step, LANGUAGE), icon=messagebox.WARNING):
            if is_extracting:
                messagebox.showinfo(Reversal.REVERSAL_TEXT[3][LANGUAGE][0], Reversal.REVERSAL_TEXT[3][LANGUAGE][1])
            while is_extracting:
                pass  # Freeze app after showing a message while files are extracting to be able to reverse
            # self.main_thread.resume()
            kill = True
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
