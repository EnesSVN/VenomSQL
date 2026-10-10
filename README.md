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
- **UNION-based SQLi** — extracts data directly from response (single request per query)
- **Auto password length detection** — detects length before brute forcing
- **Binary search extraction** — ~7 requests per character instead of 70+ (brute force)
- **CLI support** — runnable via `python -m VenomSQL`
- **Proxy support** — route traffic through Burp Suite or any HTTP proxy
- **Auto-detect DB** — fingerprint the backend database automatically
- **Request timeout** — configurable timeout to prevent hanging requests

## Project Structure

```
VenomSQL/
├── __init__.py      # Package exports
├── __main__.py      # CLI entry point
├── main.py          # BaseSQLi — base class, send(), detect_length(), build_condition_payload()
├── dbConfig.py      # Database-specific syntax configurations
├── blindError.py    # Blind SQLi (error-based) module
├── blindBoolean.py  # Blind SQLi (boolean-based) module
├── blindTime.py     # Blind SQLi (time-based) module
├── unionBased.py    # UNION-based SQLi module
├── detectDb.py      # Auto-detect database type module
├── README.md        # Documentation
└── .gitignore
```

## Usage

### Python API

```python
from VenomSQL import BlindErrorBased

inject_point = {"location": "cookie", "param": "TrackingId"}
extra_cookies = {"session": "xyz789"}

sqli = BlindErrorBased(
    url="https://target.com",
    inject_point=inject_point,
    targetTable="users",
    db_type="oracle",
    extra_cookies=extra_cookies,
    proxy="http://127.0.0.1:8080",  # optional — route through Burp
    verify=False,                    # optional — skip SSL verification
)

sqli.extract(column="password", username="administrator")
print(sqli.found_password)
```

### CLI

```bash
python -m VenomSQL \
  --url "https://target.com" \
  --technique blind-boolean \
  --db oracle \
  --inject cookie \
  --param TrackingId \
  --table users \
  --column password \
  --username administrator \
  --signal "Welcome back!"
```

With proxy (Burp Suite):

```bash
python -m VenomSQL \
  --url "https://target.com" \
  --technique blind-boolean \
  --db oracle \
  --proxy http://127.0.0.1:8080
```

Auto-detect database type:

```bash
python -m VenomSQL \
  --url "https://target.com" \
  --technique union \
  --db auto
```

For UNION enumeration:

```bash
python -m VenomSQL \
  --url "https://target.com" \
  --technique union \
  --db mysql \
  --inject cookie \
  --param TrackingId \
  --dump-tables
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

## Current Status

The project is largely up to date with the current codebase:

- [x] Blind SQLi (Boolean-based)
- [x] Blind SQLi (Time-based)
- [x] Blind SQLi (Error-based)
- [x] Flexible injection points (cookie, URL param, POST body, header)
- [x] DB-aware concat, comment, limit_one config
- [x] Password length detection
- [x] Binary search per character (~7 requests instead of 70+)
- [x] UNION-based SQLi
- [x] CLI interface
- [x] Proxy support (route through Burp)
- [x] Auto-detect DB type
- [x] Request timeout
