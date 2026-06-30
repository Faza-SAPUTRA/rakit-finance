import csv
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from models import Transaction, Wallet, db


class FormParser:
    @staticmethod
    def decimal(value, default="0"):
        try:
            amount = Decimal(str(value or default).replace(",", ""))
        except InvalidOperation as exc:
            raise ValueError("Amount tidak valid.") from exc
        if amount < 0:
            amount = abs(amount)
        return amount

    @staticmethod
    def integer(value, default):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def date(value, default=None):
        if not value:
            return default
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
        return default


class MoneyFormatter:
    @staticmethod
    def usd(value):
        return "${:,.2f}".format(float(value or 0))

    @staticmethod
    def signed(transaction):
        sign = "+" if transaction.tx_type == "income" else "-"
        return f"{sign}{MoneyFormatter.usd(transaction.amount)}"


class WalletRepository:
    def __init__(self, user):
        self.user = user

    def active_query(self):
        return Wallet.query.filter_by(user_id=self.user.id, is_active=True).order_by(Wallet.id)

    def options(self):
        return self.active_query().all()

    def default_wallet(self):
        wallet = self.active_query().first()
        if not wallet:
            wallet = Wallet(
                user_id=self.user.id,
                name="Main Wallet",
                wallet_type="bank",
                balance=Decimal("0"),
                currency="USD",
            )
            db.session.add(wallet)
            db.session.flush()
        return wallet

    def get_owned(self, wallet_id):
        wallet = Wallet.query.filter_by(id=wallet_id, user_id=self.user.id, is_active=True).first()
        if not wallet:
            raise ValueError("Wallet tidak ditemukan.")
        return wallet

    def display_rows(self):
        tone_by_type = {"bank": "blue", "ewallet": "teal"}
        icon_by_type = {"bank": "landmark", "ewallet": "wallet"}
        return [
            {
                "id": wallet.id,
                "icon": icon_by_type.get(wallet.wallet_type, "wallet"),
                "name": wallet.name,
                "balance": wallet.balance,
                "tone": tone_by_type.get(wallet.wallet_type, "purple"),
                "wallet_type": wallet.wallet_type,
            }
            for wallet in self.options()
        ]

    def create(self, form):
        name = (form.get("name") or "").strip()
        if not name:
            raise ValueError("Nama wallet wajib diisi.")
        wallet = Wallet(
            user_id=self.user.id,
            name=name,
            wallet_type=form.get("wallet_type", "bank"),
            balance=FormParser.decimal(form.get("balance"), "0"),
            currency=form.get("currency") or "USD",
        )
        db.session.add(wallet)
        db.session.commit()
        return wallet

    def update(self, wallet_id, form):
        wallet = self.get_owned(wallet_id)
        name = (form.get("name") or "").strip()
        if not name:
            raise ValueError("Nama wallet wajib diisi.")
        wallet.name = name
        wallet.wallet_type = form.get("wallet_type", wallet.wallet_type)
        wallet.balance = FormParser.decimal(form.get("balance"), wallet.balance)
        wallet.currency = form.get("currency") or wallet.currency
        db.session.commit()
        return wallet

    def delete(self, wallet_id):
        wallet = self.get_owned(wallet_id)
        has_transactions = Transaction.query.filter_by(user_id=self.user.id, wallet_id=wallet.id).first() is not None
        if has_transactions:
            wallet.is_active = False
        else:
            db.session.delete(wallet)
        db.session.commit()


class TransactionRepository:
    def __init__(self, user):
        self.user = user
        self.wallets = WalletRepository(user)

    def _base_query(self, search=""):
        rows = Transaction.query.options(joinedload(Transaction.wallet)).filter_by(user_id=self.user.id)
        if search:
            like = f"%{search}%"
            rows = rows.outerjoin(Wallet).filter(
                or_(
                    Transaction.category.ilike(like),
                    Transaction.description.ilike(like),
                    Transaction.tx_type.ilike(like),
                    Wallet.name.ilike(like),
                )
            )
        return rows.order_by(Transaction.tx_date.desc(), Transaction.id.desc())

    def count(self, search=""):
        return self._base_query(search).count()

    def paginated_rows(self, search="", page=1, per_page=5):
        return self._base_query(search).offset((page - 1) * per_page).limit(per_page).all()

    def export_rows(self, search=""):
        return self._base_query(search).all()

    def recent_rows(self, limit=3):
        return self._base_query().limit(limit).all()

    def get_owned(self, transaction_id):
        transaction = Transaction.query.options(joinedload(Transaction.wallet)).filter_by(
            id=transaction_id,
            user_id=self.user.id,
        ).first()
        if not transaction:
            raise ValueError("Transaksi tidak ditemukan.")
        return transaction

    def create(self, form):
        wallet = self.wallets.get_owned(FormParser.integer(form.get("wallet_id"), self.wallets.default_wallet().id))
        amount = FormParser.decimal(form.get("amount"), "0")
        if amount == 0:
            raise ValueError("Amount harus lebih dari 0.")
        transaction = Transaction(
            user_id=self.user.id,
            wallet_id=wallet.id,
            tx_type=form.get("tx_type", "expense"),
            category=form.get("category", "General"),
            description=form.get("description") or "Manual transaction",
            amount=amount,
            tx_date=FormParser.date(form.get("tx_date"), date.today()),
        )
        self._apply_to_wallet(wallet, transaction.tx_type, transaction.amount)
        db.session.add(transaction)
        db.session.commit()
        return transaction

    def update(self, transaction_id, form):
        transaction = self.get_owned(transaction_id)
        old_wallet = transaction.wallet or self.wallets.default_wallet()
        self._reverse_wallet_effect(old_wallet, transaction.tx_type, transaction.amount)

        wallet = self.wallets.get_owned(FormParser.integer(form.get("wallet_id"), old_wallet.id))
        amount = FormParser.decimal(form.get("amount"), transaction.amount)
        if amount == 0:
            raise ValueError("Amount harus lebih dari 0.")
        transaction.wallet_id = wallet.id
        transaction.tx_type = form.get("tx_type", transaction.tx_type)
        transaction.category = form.get("category", transaction.category)
        transaction.description = form.get("description") or transaction.description
        transaction.amount = amount
        transaction.tx_date = FormParser.date(form.get("tx_date"), transaction.tx_date)

        self._apply_to_wallet(wallet, transaction.tx_type, transaction.amount)
        db.session.commit()
        return transaction

    def delete(self, transaction_id):
        transaction = self.get_owned(transaction_id)
        if transaction.wallet:
            self._reverse_wallet_effect(transaction.wallet, transaction.tx_type, transaction.amount)
        db.session.delete(transaction)
        db.session.commit()

    def display_rows(self, search="", page=1, per_page=5):
        return [self._display_dict(tx) for tx in self.paginated_rows(search, page, per_page)]

    def recent_display_rows(self):
        return [
            (
                self.category_icon(tx.category, tx.tx_type),
                tx.description,
                tx.category,
                tx.tx_date.strftime("%b %d, %Y"),
                MoneyFormatter.signed(tx),
                "in" if tx.tx_type == "income" else "out",
            )
            for tx in self.recent_rows()
        ]

    def _display_dict(self, tx):
        return {
            "id": tx.id,
            "date": tx.tx_date.strftime("%b %d, %Y"),
            "date_value": tx.tx_date.isoformat(),
            "category": tx.category,
            "description": tx.description,
            "account": tx.wallet.name if tx.wallet else "Wallet",
            "wallet_id": tx.wallet_id,
            "amount": MoneyFormatter.signed(tx),
            "amount_value": "{:.2f}".format(float(tx.amount)),
            "tx_type": tx.tx_type,
            "tone": "in" if tx.tx_type == "income" else "out",
        }

    @staticmethod
    def category_icon(category, tx_type):
        if tx_type == "income":
            return "briefcase"
        icons = {
            "Shopping": "shopping-bag",
            "Food": "utensils",
            "Food & Drink": "utensils",
            "Bills": "receipt-text",
            "Transport": "car",
        }
        return icons.get(category, "wallet")

    @staticmethod
    def _apply_to_wallet(wallet, tx_type, amount):
        wallet.balance += amount if tx_type == "income" else -amount

    @staticmethod
    def _reverse_wallet_effect(wallet, tx_type, amount):
        wallet.balance -= amount if tx_type == "income" else -amount


class DashboardService:
    def __init__(self, user):
        self.user = user
        self.transactions = TransactionRepository(user)
        self.wallets = WalletRepository(user)

    def stats(self):
        total_balance = db.session.query(func.coalesce(func.sum(Wallet.balance), 0)).filter_by(
            user_id=self.user.id,
            is_active=True,
        ).scalar()
        total_income = self.transaction_sum("income")
        total_expense = self.transaction_sum("expense")
        return [
            {"label": "Total Balance", "value": MoneyFormatter.usd(total_balance), "trend": "2.4%", "tone": "green", "icon": "landmark"},
            {"label": "Monthly Income", "value": MoneyFormatter.usd(total_income), "trend": "1.2%", "tone": "blue", "icon": "trending-down"},
            {"label": "Monthly Expense", "value": MoneyFormatter.usd(total_expense), "trend": "5.0%", "tone": "orange", "icon": "shopping-cart"},
        ]

    def transaction_sum(self, tx_type):
        return (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter_by(user_id=self.user.id, tx_type=tx_type)
            .scalar()
        )


class CsvStatementImporter:
    def __init__(self, user):
        self.user = user
        self.transactions = TransactionRepository(user)

    def import_file(self, upload):
        if not upload or not upload.filename:
            raise ValueError("Pilih file CSV statement terlebih dahulu.")
        if not upload.filename.lower().endswith(".csv"):
            raise ValueError("Import demo saat ini mendukung CSV. File .xlsx bisa ditambahkan nanti.")

        text = upload.stream.read().decode("utf-8-sig")
        reader = csv.DictReader(StringIO(text))
        imported = 0
        for row in reader:
            amount_raw = row.get("amount") or row.get("Amount") or "0"
            try:
                amount = FormParser.decimal(amount_raw)
            except ValueError:
                continue
            tx_type = (row.get("type") or row.get("Type") or "").lower()
            if tx_type not in {"income", "expense"}:
                tx_type = "income" if Decimal(str(amount_raw).replace(",", "")) >= 0 else "expense"
            wallet = self._wallet_for(row.get("wallet") or row.get("Wallet"))
            form = {
                "wallet_id": wallet.id,
                "tx_type": tx_type,
                "category": row.get("category") or row.get("Category") or "Imported",
                "description": row.get("description") or row.get("Description") or "Imported transaction",
                "amount": amount,
                "tx_date": row.get("date") or row.get("Date") or date.today().isoformat(),
            }
            self.transactions.create(form)
            imported += 1
        return imported

    def _wallet_for(self, wallet_name):
        repository = WalletRepository(self.user)
        if wallet_name:
            wallet = Wallet.query.filter_by(user_id=self.user.id, name=wallet_name, is_active=True).first()
            if wallet:
                return wallet
        return repository.default_wallet()


class InvestmentAsset(ABC):
    key = ""
    label = ""
    rate = 0.0
    icon = "landmark"
    description = ""
    outlook = ""

    @abstractmethod
    def calculate_projection(self, initial, monthly, years):
        raise NotImplementedError

    def metadata(self):
        return {
            "label": self.label,
            "rate": self.rate,
            "icon": self.icon,
            "description": self.description,
            "outlook": self.outlook,
        }

    def _compound_projection(self, initial, monthly, years):
        balance = float(initial)
        rows = []
        labels = []
        balances = []
        total_contribution = float(initial)
        total_interest = 0.0

        for year in range(1, years + 1):
            annual_contribution = monthly * 12
            balance += annual_contribution
            interest = balance * self.rate
            balance += interest
            total_contribution += annual_contribution
            total_interest += interest
            labels.append(str(date.today().year + year - 1))
            balances.append(round(balance, 2))
            rows.append(
                {
                    "year": f"Year {year}",
                    "contribution": annual_contribution,
                    "interest": round(interest, 2),
                    "balance": round(balance, 2),
                }
            )

        return {
            "labels": labels,
            "balances": balances,
            "total_contribution": round(total_contribution, 2),
            "interest_earned": round(total_interest, 2),
            "estimated_total": round(balance, 2),
            "rows": rows[:5],
        }


class MutualFundAsset(InvestmentAsset):
    key = "mutual_fund"
    label = "Mutual Fund"
    rate = 0.085
    icon = "landmark"
    description = "Diversified portfolio managed by experts"
    outlook = "Based on current trends, Mutual Funds are expected to yield 8-12% APR over the next decade."

    def calculate_projection(self, initial, monthly, years):
        return self._compound_projection(initial, monthly, years)


class GoldAsset(InvestmentAsset):
    key = "gold"
    label = "Gold"
    rate = 0.055
    icon = "banknote"
    description = "Safe-haven commodity for stability"
    outlook = "Gold is modeled with steadier 4-7% APR growth and lower volatility."

    def calculate_projection(self, initial, monthly, years):
        return self._compound_projection(initial, monthly, years)


class CryptoAsset(InvestmentAsset):
    key = "crypto"
    label = "Crypto"
    rate = 0.14
    icon = "bitcoin"
    description = "High-growth digital asset volatility"
    outlook = "Crypto projection uses higher 14% APR potential, with higher risk and volatility."

    def calculate_projection(self, initial, monthly, years):
        return self._compound_projection(initial, monthly, years)


class InvestmentProjectionCalculator:
    def __init__(self):
        self.assets = {asset.key: asset for asset in (MutualFundAsset(), GoldAsset(), CryptoAsset())}

    def asset_metadata(self):
        return {key: asset.metadata() for key, asset in self.assets.items()}

    def calculate(self, initial, monthly, years, asset_key="mutual_fund"):
        asset = self.assets.get(asset_key, self.assets["mutual_fund"])
        return asset.calculate_projection(initial, monthly, years)


class MarketDataService:
    def cards(self, query=""):
        cards = [
            ("BITCOIN (BTC/USD)", "$65,240.50", "+2.5%", "up"),
            ("ETHEREUM (ETH/USD)", "$3,512.20", "-1.2%", "down"),
            ("US 30Y TREASURY", "4.52%", "+0.05%", "up"),
            ("INDOGB 10Y BOND", "6.84%", "-0.02%", "down"),
        ]
        return self._filter(cards, query)

    def news(self, query=""):
        news = [
            (
                "CNBC",
                "2 hours ago",
                "Global Markets React to Fed Policy Shift and Inflation Targets",
                "Investors are pivoting as treasury yields fluctuate following the latest central bank announcement regarding long-term inflation targets and potential rate adjustments.",
            ),
            (
                "FINANCIALJUICE",
                "4 hours ago",
                "Oil Prices Surge Amidst Tensions in Key Transit Corridors",
                "Energy markets are on high alert as diplomatic escalations threaten major supply routes. Crude futures rose by 1.5% in early morning trading.",
            ),
            (
                "CNBC",
                "5 hours ago",
                "European Tech Stocks Hit 52-Week High as Sector Sentiment Improves",
                "Renewed interest in semiconductor manufacturing and AI software development has propelled several major European tech conglomerates to record heights this quarter.",
            ),
        ]
        return self._filter(news, query)

    @staticmethod
    def _filter(rows, query):
        if not query:
            return rows
        needle = query.lower()
        return [row for row in rows if any(needle in str(value).lower() for value in row)]
