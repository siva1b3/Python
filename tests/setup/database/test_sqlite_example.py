"""Toy test using an in-memory SQLite database."""

import sqlite3
from contextlib import closing


def test_sqlite_returns_query_parameter() -> None:
    with closing(sqlite3.connect(":memory:")) as database:
        row = database.execute("SELECT ?", ("hello",)).fetchone()

    assert row == ("hello",)
