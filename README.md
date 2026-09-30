# VenomSQL

Modular SQL injection automation tool.

## Features

- **Modular architecture** — each SQLi technique is a separate module
- **Multi-DB support** — Oracle, MySQL, PostgreSQL, MSSQL, SQLite, MariaDB
- **Blind SQLi (Error-based)** — extracts data character by character using conditional errors
- **Blind SQLi (Boolean-based)** — extracts data using true/false page response signals
- **Blind SQLi (Time-based)** — extracts data using response time delays

## Project Structure

```
VenomSQL/
├── main.py          # BaseSQLi — base class for all techniques
├── dbConfig.py      # Database-specific syntax configurations
├── blindError.py    # Blind SQLi (error-based) module
├── blindBoolean.py  # Blind SQLi (boolean-based) module
├── blindTime.py     # Blind SQLi (time-based) module
└── .gitignore
```

## Usage

```python
from blindError import BlindErrorBased

cookie = {"TrackingId": "abc123", "session": "xyz789"}
sqli = BlindErrorBased(url="https://target.com", cookie=cookie, targetTable="users", db_type="oracle")
sqli.extract(column="password", username="administrator")
print(sqli.found_password)
```

## Roadmap

- [x] Blind SQLi (Boolean-based)
- [x] Blind SQLi (Time-based)
- [ ] Flexible injection points (cookie, URL param, POST body, header)
- [ ] Password length detection
- [ ] Binary search per character (6 requests instead of 36)
- [ ] UNION-based SQLi
- [ ] Proxy support (route through Burp)
- [ ] CLI interface
- [ ] Auto-detect DB type
