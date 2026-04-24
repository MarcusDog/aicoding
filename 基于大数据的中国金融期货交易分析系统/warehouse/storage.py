from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd
from duckdb import CatalogException

from project_config import DUCKDB_PATH, GOLD_DIR, SILVER_DIR, ensure_directories


class WarehouseStore:
    def __init__(self, db_path: Path = DUCKDB_PATH) -> None:
        ensure_directories()
        self.db_path = db_path

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.db_path))

    def write_table(self, table_name: str, df: pd.DataFrame, layer: str = "silver") -> Path:
        ensure_directories()
        base_dir = SILVER_DIR if layer == "silver" else GOLD_DIR
        base_dir.mkdir(parents=True, exist_ok=True)
        file_path = base_dir / f"{table_name}.parquet"
        if df.empty:
            df = pd.DataFrame(columns=df.columns)
        df.to_parquet(file_path, index=False)
        with self._connect() as conn:
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path.as_posix()}')")
        return file_path

    def table_exists(self, table_name: str) -> bool:
        with self._connect() as conn:
            result = conn.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'main' AND table_name = ?
                """,
                [table_name],
            ).fetchone()
        return bool(result and result[0])

    def read_table(self, table_name: str, empty_ok: bool = False) -> pd.DataFrame:
        if empty_ok and not self.table_exists(table_name):
            return pd.DataFrame()
        with self._connect() as conn:
            try:
                return conn.execute(f"SELECT * FROM {table_name}").fetchdf()
            except CatalogException:
                if empty_ok:
                    return pd.DataFrame()
                raise

    def list_tables(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'main'
                ORDER BY table_name
                """
            ).fetchall()
        return [row[0] for row in rows]

    def table_row_count(self, table_name: str) -> int:
        if not self.table_exists(table_name):
            return 0
        with self._connect() as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return int(row[0]) if row else 0

    def query(self, sql: str) -> pd.DataFrame:
        with self._connect() as conn:
            return conn.execute(sql).fetchdf()
