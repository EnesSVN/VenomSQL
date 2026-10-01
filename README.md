# VenomSQL

Modular SQL injection automation tool.

## Features

- **Modular architecture** — each SQLi technique is a separate module
- **Multi-DB support** — Oracle, MySQL, PostgreSQL, MSSQL, SQLite, MariaDB
- **Flexible injection points** — cookie, URL parameter, POST body, header
- **DB-aware config** — substr, concat, comment, sleep, limit per database
- **Blind SQLi (Error-based)** — extracts data using conditional errors (500 vs 200)
- **Blind SQLi (Boolean-based)** — extracts data using true/false page response signals
- **Blind SQLi (Time-based)** — extracts data using response time delays
- **Auto password length detection** — detects length before brute forcing
- **Extended charset** — lowercase, uppercase, digits, and special characters

## Project Structure

```
VenomSQL/
├── __init__.py      # Package exports
├── main.py          # BaseSQLi — base class, send(), detect_length(), build_condition_payload()
├── dbConfig.py      # Database-specific syntax configurations
├── blindError.py    # Blind SQLi (error-based) module
├── blindBoolean.py  # Blind SQLi (boolean-based) module
├── blindTime.py     # Blind SQLi (time-based) module
└── .gitignore
```

## Usage

```python
from VenomSQL import BlindErrorBased

inject_point = {"location": "cookie", "param": "TrackingId"}
extra_cookies = {"session": "xyz789"}

sqli = BlindErrorBased(
    url="https://target.com",
    inject_point=inject_point,
    targetTable="users",
    db_type="oracle",
    extra_cookies=extra_cookies
)
sqli.extract(column="password", username="administrator")
print(sqli.found_password)
```

## Supported Databases

| DB | substr | concat | comment | sleep |
|----|--------|--------|---------|-------|
| Oracle | SUBSTR | \|\| | -- | DBMS_PIPE.RECEIVE_MESSAGE |
| MySQL | SUBSTRING | CONCAT | # | SLEEP |
| PostgreSQL | SUBSTRING | \|\| | -- | pg_sleep |
| MSSQL | SUBSTRING | + | -- | WAITFOR DELAY |
| SQLite | SUBSTR | \|\| | -- | - |
| MariaDB | SUBSTRING | CONCAT | # | SLEEP |

## Roadmap

- [x] Blind SQLi (Boolean-based)
- [x] Blind SQLi (Time-based)
- [x] Flexible injection points (cookie, URL param, POST body, header)
- [x] DB-aware concat, comment, limit_one config
- [x] Password length detection
- [ ] Binary search per character (6 requests instead of 36)
- [ ] UNION-based SQLi
- [ ] Proxy support (route through Burp)
- [ ] CLI interface
- [ ] Auto-detect DB type
