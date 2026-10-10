"""Unit tests for SQLite database manager, query execution, and metric reconciliation."""

import pytest
import pandas as pd
from src.database.db_manager import DatabaseManager, init_database
from src.data.loader import load_raw_data
from src.utils.config import Config


def test_database_init():
    """Verify SQLite database initialization and customers table count."""
    db = init_database()
    assert Config.SQLITE_DB_PATH.exists()

    df_count = db.execute_query("SELECT COUNT(*) AS total FROM customers")
    assert df_count.iloc[0]["total"] == 10000


def test_sql_named_queries_execution():
    """Verify all 9 analytical queries in churn_queries.sql run successfully."""
    db = DatabaseManager()
    queries = db.load_named_queries()
    assert len(queries) >= 9

    for qname in queries:
        df_res = db.execute_named_query(qname)
        assert isinstance(df_res, pd.DataFrame)
        assert len(df_res) > 0, f"Query {qname} returned empty result"


def test_sql_reconciliation_with_raw_data():
    """Reconcile SQL metrics against raw DataFrame ground truth."""
    db = DatabaseManager()
    sql_summary = db.execute_named_query("executive_summary").iloc[0]
    df_raw = load_raw_data()

    assert int(sql_summary["TotalCustomers"]) == len(df_raw)
    assert int(sql_summary["ChurnedCustomers"]) == int(df_raw["Exited"].sum())
    assert int(sql_summary["RetainedCustomers"]) == int((df_raw["Exited"] == 0).sum())
    assert round(float(sql_summary["ChurnRate"]), 4) == round(float(df_raw["Exited"].mean()), 4)
