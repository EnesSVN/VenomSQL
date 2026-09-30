DB_CONFIG = {
    "oracle": {
        "substr": "SUBSTR",
        "error_trigger": "TO_CHAR(1/0)",
        "from_dual": " FROM dual",
        "sleep": "DBMS_LOCK.SLEEP",
    },
    "mysql": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
        "sleep": "SLEEP",
    },
    "postgresql": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
        "sleep": "pg_sleep",
    },
    "mssql": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
        "sleep": "WAITFOR DELAY",
    },
    "sqlite": {
        "substr": "SUBSTR",
        "error_trigger": "1/0",
        "from_dual": "",
        "sleep": "sqlite_sleep",
    },
    "mariadb": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
        "sleep": "SLEEP",
    },
}