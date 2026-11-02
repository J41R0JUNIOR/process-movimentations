import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.database import connect, insert_transactions
from app.domain.classification import classify, is_savings_movement
from app.read import _parse_cents, read_credit_csv


class FinancialPipelineTests(unittest.TestCase):
    def test_parse_cents_rounds_to_nearest_cent(self) -> None:
        self.assertEqual(_parse_cents("297.17", Path("test.csv"), 2), 29717)
        self.assertEqual(_parse_cents("-0.01", Path("test.csv"), 3), -1)
        self.assertEqual(_parse_cents("1.234", Path("test.csv"), 4), 123)
        self.assertEqual(_parse_cents("1.235", Path("test.csv"), 5), 124)
        self.assertEqual(_parse_cents("-1.235", Path("test.csv"), 6), -124)

    def test_parse_cents_rejects_int32_overflow(self) -> None:
        with self.assertRaises(ValueError):
            _parse_cents("21474836.48", Path("test.csv"), 2)

    def test_read_credit_csv_normalizes_expenses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credit.csv"
            path.write_text(
                "date,title,amount\n2026-01-24,Dm*Spotify,\"12,90\"\n",
                encoding="utf-8",
            )
            transaction = read_credit_csv(path)[0]
            self.assertEqual(transaction["date"], "2026-01-24")
            self.assertEqual(transaction["value"], -1290)
            self.assertEqual(transaction["product"], "credit")

    def test_read_credit_csv_handles_thousands_and_payments(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "credit.csv"
            path.write_text(
                "date,title,amount\n2026-01-24,Pagamento recebido,\"- 1.385,84\"\n",
                encoding="utf-8",
            )
            transaction = read_credit_csv(path)[0]
            self.assertEqual(transaction["value"], 138584)

    def test_savings_movements_are_excluded(self) -> None:
        for description in ("Aplicação RDB", "Resgate RDB"):
            self.assertTrue(is_savings_movement(description))
        self.assertFalse(is_savings_movement("Transferência enviada pelo Pix"))

    def test_classification_marks_card_payment(self) -> None:
        result = classify("Pagamento de fatura", -100)
        self.assertEqual(result.transaction_type, "transfer")
        self.assertTrue(result.is_internal)
        self.assertTrue(result.is_ignored)
        self.assertTrue(result.is_card_payment)

    def test_database_deduplicates_same_source_and_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "financial.db")
            transaction = {
                "id": "transaction-1",
                "date": "2026-01-01",
                "value": -100,
                "description": "Teste",
                "source": "nubank",
                "product": "account",
                "source_file": "test.csv",
                "transaction_type": "expense",
                "category": "não classificado",
                "is_internal": 0,
                "is_ignored": 0,
                "is_card_payment": 0,
                "ignore_reason": None,
            }
            self.assertEqual(insert_transactions(connection, [transaction]), 1)
            self.assertEqual(insert_transactions(connection, [transaction]), 0)
            count = connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
            self.assertEqual(count, 1)
            connection.close()


if __name__ == "__main__":
    unittest.main()
