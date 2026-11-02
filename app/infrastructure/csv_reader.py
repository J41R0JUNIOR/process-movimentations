from pathlib import Path

from app.read import read_credit_csv, read_csv


class NubankCsvReader:
    source = "nubank"

    def read_folder(self, input_folder: Path) -> list[dict]:
        transactions = []
        for file in sorted(input_folder.glob("*/*/*.csv")):
            relative_path = file.relative_to(input_folder)
            source, product = relative_path.parts[:2]
            print(f"Reading: {relative_path}")
            reader = read_credit_csv if product == "credit" else read_csv
            transactions.extend(
                {
                    **transaction,
                    "source": source,
                    "product": product,
                    "source_file": relative_path.as_posix(),
                }
                for transaction in reader(file)
            )
        return transactions
