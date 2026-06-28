from abc import ABC, abstractmethod
from datetime import datetime
from io import BytesIO

import pandas as pd

from app.models.transaction import Transaction


def _rupiah_to_cents(value) -> int:
    if pd.isna(value):
        return 0
    text = str(value).replace("Rp", "").replace(".", "").replace(",", "").strip()
    if not text or text.lower() == "nan":
        return 0
    return int(float(text)) * 100


def _read_table(file_storage):
    raw = file_storage.read()
    file_storage.seek(0)
    filename = (file_storage.filename or "").lower()
    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(raw))
    return pd.read_csv(BytesIO(raw))


class TransactionParser(ABC):
    """Abstract parser. Concrete banks map their own columns in parse()."""

    source_name = "generic"

    @abstractmethod
    def parse(self, file_storage, user_id: int | None = None) -> list[Transaction]:
        """Convert uploaded bank data into Transaction objects."""


class BcaParser(TransactionParser):
    source_name = "bca"

    def parse(self, file_storage, user_id: int | None = None) -> list[Transaction]:
        frame = _read_table(file_storage)
        normalized = {column.lower().strip(): column for column in frame.columns}
        date_col = normalized.get("tanggal") or normalized.get("date")
        desc_col = normalized.get("keterangan") or normalized.get("description")
        debit_col = normalized.get("debit")
        credit_col = normalized.get("credit") or normalized.get("kredit")

        transactions = []
        for _, row in frame.iterrows():
            debit = _rupiah_to_cents(row.get(debit_col, 0)) if debit_col else 0
            credit = _rupiah_to_cents(row.get(credit_col, 0)) if credit_col else 0
            amount = credit or debit
            if not amount:
                continue
            transaction_type = "income" if credit else "expense"
            transactions.append(
                Transaction(
                    user_id=user_id or 0,
                    merchant=str(row.get(desc_col, "BCA Transaction"))[:160],
                    category="Imported",
                    amount_cents=amount,
                    transaction_type=transaction_type,
                    source=self.source_name,
                    occurred_on=pd.to_datetime(row.get(date_col, datetime.utcnow())).date(),
                )
            )
        return transactions


class GopayParser(TransactionParser):
    source_name = "gopay"

    def parse(self, file_storage, user_id: int | None = None) -> list[Transaction]:
        frame = _read_table(file_storage)
        normalized = {column.lower().strip(): column for column in frame.columns}
        date_col = normalized.get("transaction date") or normalized.get("date") or normalized.get("tanggal")
        merchant_col = normalized.get("merchant") or normalized.get("description") or normalized.get("deskripsi")
        amount_col = normalized.get("amount") or normalized.get("nominal")
        direction_col = normalized.get("type") or normalized.get("direction")

        transactions = []
        for _, row in frame.iterrows():
            amount = _rupiah_to_cents(row.get(amount_col, 0)) if amount_col else 0
            if not amount:
                continue
            direction = str(row.get(direction_col, "expense")).lower() if direction_col else "expense"
            transaction_type = "income" if direction in {"in", "income", "topup", "credit"} else "expense"
            transactions.append(
                Transaction(
                    user_id=user_id or 0,
                    merchant=str(row.get(merchant_col, "GoPay Transaction"))[:160],
                    category="E-Wallet",
                    amount_cents=amount,
                    transaction_type=transaction_type,
                    source=self.source_name,
                    occurred_on=pd.to_datetime(row.get(date_col, datetime.utcnow())).date(),
                )
            )
        return transactions
