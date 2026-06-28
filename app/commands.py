from datetime import date, timedelta

from app.extensions import db
from app.models.account import AssetAccount, LiabilityAccount
from app.models.transaction import Transaction
from app.models.user import User


def register(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database initialized.")

    @app.cli.command("seed-demo")
    def seed_demo():
        db.drop_all()
        db.create_all()

        user = User(name="Demo Founder", email="demo@rakit.local")
        user.set_password("password")
        db.session.add(user)
        db.session.flush()

        accounts = [
            AssetAccount(user_id=user.id, name="BCA Everyday", institution="BCA", balance_cents=685000000),
            AssetAccount(user_id=user.id, name="GoPay Wallet", institution="GoPay", balance_cents=83000000),
            AssetAccount(user_id=user.id, name="Reksa Dana Growth", institution="Bibit", balance_cents=425000000),
            LiabilityAccount(user_id=user.id, name="Credit Card", institution="Visa", balance_cents=57500000),
            LiabilityAccount(user_id=user.id, name="Laptop Installment", institution="Kredivo", balance_cents=35000000),
        ]
        db.session.add_all(accounts)

        today = date.today()
        transactions = [
            ("Kopi Kenangan", "Food", 4800000, "expense", today - timedelta(days=1), "manual"),
            ("Gojek Ride", "Transport", 3200000, "expense", today - timedelta(days=2), "gopay"),
            ("Salary", "Income", 2250000000, "income", today - timedelta(days=3), "bca"),
            ("Tokopedia Groceries", "Shopping", 31500000, "expense", today - timedelta(days=4), "manual"),
            ("PLN Electricity", "Bills", 26500000, "expense", today - timedelta(days=5), "bca"),
            ("Spotify", "Subscriptions", 5490000, "expense", today - timedelta(days=6), "manual"),
            ("Emergency Fund Interest", "Income", 12600000, "income", today - timedelta(days=7), "bca"),
            ("Lunch Meeting", "Food", 18200000, "expense", today - timedelta(days=8), "ocr"),
        ]
        db.session.add_all(
            [
                Transaction(
                    user_id=user.id,
                    merchant=merchant,
                    category=category,
                    amount_cents=amount,
                    transaction_type=kind,
                    occurred_on=occurred,
                    source=source,
                )
                for merchant, category, amount, kind, occurred, source in transactions
            ]
        )
        db.session.commit()
        print("Seeded demo user: demo@rakit.local / password")

