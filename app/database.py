import sqlite3
from pathlib import Path
from typing import Iterable

DATABASE_PATH = Path("data/database/financial.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS imports (
    id INTEGER PRIMARY KEY,
    source_file TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    row_count INTEGER NOT NULL,
    inserted_count INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'failed'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT NOT NULL,
    date TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    description TEXT NOT NULL,
    source TEXT NOT NULL,
    product TEXT NOT NULL DEFAULT 'account',
    source_file TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    category TEXT NOT NULL,
    is_internal INTEGER NOT NULL DEFAULT 0 CHECK (is_internal IN (0, 1)),
    is_ignored INTEGER NOT NULL DEFAULT 0 CHECK (is_ignored IN (0, 1)),
    ignore_reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source, id)
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
"""


def connect(path: Path = DATABASE_PATH) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(transactions)")
    }
    if "product" not in columns:
        connection.execute(
            "ALTER TABLE transactions ADD COLUMN product TEXT NOT NULL DEFAULT 'account'"
        )
    connection.execute(
        """
        UPDATE transactions
        SET category = 'cofrinho',
            is_internal = 1,
            is_ignored = 1,
            ignore_reason = CASE
                WHEN lower(description) LIKE '%aplicação rdb%'
                    THEN 'Aplicação no cofrinho'
                ELSE 'Resgate do cofrinho'
            END
        WHERE lower(description) LIKE '%aplicação rdb%'
           OR lower(description) LIKE '%resgate rdb%'
        """
    )
    connection.commit()
    return connection


def insert_transactions(
    connection: sqlite3.Connection,
    transactions: Iterable[dict],
) -> int:
    inserted = 0
    for transaction in transactions:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO transactions (
                id, date, amount_cents, description, source, product, source_file,
                transaction_type, category, is_internal, is_ignored, ignore_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                transaction["id"],
                transaction["date"],
                transaction["value"],
                transaction["description"],
                transaction["source"],
                transaction["product"],
                transaction["source_file"],
                transaction["transaction_type"],
                transaction["category"],
                transaction["is_internal"],
                transaction["is_ignored"],
                transaction["ignore_reason"],
            ),
        )
        inserted += cursor.rowcount
    return inserted
