from pathlib import Path

import duckdb
import sqlglot
from sqlglot import exp


ALLOWED_TABLES = {"v_complaints"}


def guard_sql(sql: str) -> str:
    """Allow exactly one SELECT against v_complaints, capped at 200 rows."""
    statements = sqlglot.parse(sql, read="duckdb")
    statements = [s for s in statements if s is not None]

    if len(statements) != 1:
        raise ValueError("Exactly one SQL statement is allowed")

    tree = statements[0]

    if not isinstance(tree, exp.Select):
        raise ValueError("Only SELECT queries are allowed")

    ctes = {
        c.alias_or_name.lower()
        for c in tree.find_all(exp.CTE)
    }

    tables = {
        t.name.lower()
        for t in tree.find_all(exp.Table)
    } - ctes

    if not tables or not tables <= ALLOWED_TABLES:
        raise ValueError(f"Table(s) not allowed: {tables}")

    limit_node = tree.args.get("limit")

    if limit_node is None:
        tree = sqlglot.parse_one(
            f"SELECT * FROM ({tree.sql(dialect='duckdb')}) "
            "AS safe_query LIMIT 200",
            read="duckdb",
        )
    else:
        try:
            n = int(limit_node.expression.this)
        except Exception as exc:
            raise ValueError("LIMIT must be a numeric literal") from exc

        if n > 200:
            tree.set(
                "limit",
                exp.Limit(expression=exp.Literal.number(200))
            )

    return tree.sql(dialect="duckdb")


def run_sql(sql: str) -> list[dict]:
    """Execute guarded SQL using a read-only DuckDB connection."""
    safe_sql = guard_sql(sql)

    root = Path(__file__).resolve().parents[1]
    db_path = root / "data" / "complaintiq.duckdb"

    if not db_path.is_file():
        raise FileNotFoundError(f"DuckDB database missing: {db_path}")

    con = duckdb.connect(str(db_path), read_only=True)
    try:
        return con.execute(safe_sql).fetchdf().to_dict("records")
    finally:
        con.close()
