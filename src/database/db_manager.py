"""SQLite Database Manager for analytical queries and prediction persistence.

Provides schema creation, table ingestion, query execution, and metric reconciliation.
"""

from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from src.utils.config import Config


class DatabaseManager:
    """Manages SQLite analytical connection, data population, and query execution."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path if db_path is not None else Config.SQLITE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a SQLite connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_schema(self, schema_path: Optional[Path] = None) -> None:
        """Execute DDL script to create database tables and indexes."""
        script_path = (
            schema_path if schema_path is not None else Config.SQL_DIR / "schema.sql"
        )
        with open(script_path, "r", encoding="utf-8") as f:
            ddl_sql = f.read()

        with self.get_connection() as conn:
            conn.executescript(ddl_sql)
            conn.commit()

    def populate_customers(self, df: pd.DataFrame) -> int:
        """Populate the customers table from a pandas DataFrame."""
        with self.get_connection() as conn:
            # Overwrite customers table
            df.to_sql("customers", conn, if_exists="replace", index=False)
            conn.commit()
        return len(df)

    def load_named_queries(
        self, sql_filepath: Optional[Path] = None
    ) -> Dict[str, str]:
        """Parse named SQL queries from a .sql file formatted with '-- NAME: <query_name>'."""
        path = (
            sql_filepath
            if sql_filepath is not None
            else Config.SQL_DIR / "churn_queries.sql"
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        queries: Dict[str, str] = {}
        current_name = None
        current_lines = []

        for line in content.splitlines():
            if line.strip().startswith("-- NAME:"):
                if current_name and current_lines:
                    queries[current_name] = "\n".join(current_lines).strip()
                current_name = line.replace("-- NAME:", "").strip()
                current_lines = []
            elif not line.strip().startswith("--") or current_name:
                current_lines.append(line)

        if current_name and current_lines:
            queries[current_name] = "\n".join(current_lines).strip()

        return queries

    def execute_query(self, sql: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """Execute arbitrary SELECT SQL and return results as DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(sql, conn, params=params)

    def execute_named_query(self, query_name: str) -> pd.DataFrame:
        """Execute a parsed named query from churn_queries.sql."""
        queries = self.load_named_queries()
        if query_name not in queries:
            raise KeyError(
                f"Query '{query_name}' not found. Available: {list(queries.keys())}"
            )
        return self.execute_query(queries[query_name])

    def store_predictions(
        self,
        customer_ids: List[int],
        probabilities: List[float],
        risk_categories: List[str],
        model_version: str = "v1.0",
    ) -> int:
        """Insert or replace customer predictions into the customer_predictions table."""
        records = [
            (int(cid), float(prob), str(cat), str(model_version))
            for cid, prob, cat in zip(customer_ids, probabilities, risk_categories)
        ]
        sql = """
        INSERT OR REPLACE INTO customer_predictions (CustomerId, PredictedProbability, RiskCategory, ModelVersion)
        VALUES (?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.executemany(sql, records)
            conn.commit()
        return len(records)


def init_database() -> DatabaseManager:
    """Helper to initialize schema and populate with processed churn data."""
    manager = DatabaseManager()
    manager.initialize_schema()

    if Config.PROCESSED_DATA_PATH.exists():
        df = pd.read_csv(Config.PROCESSED_DATA_PATH)
    else:
        from src.data.loader import load_raw_data
        from src.features.engineering import engineer_features_df

        df = engineer_features_df(load_raw_data())

    manager.populate_customers(df)
    return manager
