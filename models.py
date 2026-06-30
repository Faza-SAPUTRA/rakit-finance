from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("ix_users_email", "email"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallets = db.relationship("Wallet", back_populates="user", cascade="all, delete-orphan", lazy=True)
    transactions = db.relationship("Transaction", back_populates="user", cascade="all, delete-orphan", lazy=True)
    budgets = db.relationship("Budget", back_populates="user", cascade="all, delete-orphan", lazy=True)


class Wallet(db.Model):
    __tablename__ = "wallets"
    __table_args__ = (
        db.CheckConstraint("balance >= -999999999999.99", name="ck_wallet_balance_reasonable"),
        db.Index("ix_wallets_user_active", "user_id", "is_active"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    wallet_type = db.Column(db.String(60), nullable=False, default="bank")
    balance = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    currency = db.Column(db.String(12), nullable=False, default="IDR")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship("User", back_populates="wallets")
    transactions = db.relationship("Transaction", back_populates="wallet", lazy=True)


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        db.CheckConstraint("amount >= 0", name="ck_transactions_amount_non_negative"),
        db.CheckConstraint("tx_type in ('income', 'expense')", name="ck_transactions_type"),
        db.Index("ix_transactions_user_date", "user_id", "tx_date"),
        db.Index("ix_transactions_wallet", "wallet_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"))
    tx_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(180), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    tx_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="transactions")
    wallet = db.relationship("Wallet", back_populates="transactions")


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        db.UniqueConstraint("user_id", "category", name="uq_budgets_user_category"),
        db.CheckConstraint("monthly_limit >= 0", name="ck_budgets_limit_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    monthly_limit = db.Column(db.Numeric(14, 2), nullable=False)
    spent = db.Column(db.Numeric(14, 2), nullable=False, default=0)

    user = db.relationship("User", back_populates="budgets")
