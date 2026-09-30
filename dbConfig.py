DB_CONFIG = {
    "oracle": {
        "substr": "SUBSTR",
        "error_trigger": "TO_CHAR(1/0)",
        "from_dual": " FROM dual",
    },
    "mysql": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
    },
    "postgresql": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
    },
    "mssql": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
    },
    "sqlite": {
        "substr": "SUBSTR",
        "error_trigger": "1/0",
        "from_dual": "",
    },
    "mariadb": {
        "substr": "SUBSTRING",
        "error_trigger": "1/0",
        "from_dual": "",
    },
}