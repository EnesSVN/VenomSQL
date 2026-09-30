
class BaseSQLi:
    def __init__(self, url, cookie, targetTable,db_type="oracle"):
        self.url = url
        self.cookie = cookie
        self.targetTable = targetTable
        self.db_type = db_type

    def extract(self, column):
        raise NotImplementedError("Subclasses should implement this method.")


