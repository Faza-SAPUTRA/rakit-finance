from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallets = db.relationship("Wallet", backref="user", lazy=True)
    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    wallet_type = db.Column(db.String(60), nullable=False, default="bank")
    balance = db.Column(db.Numeric(14, 2), nullable=False, default=0)
    currency = db.Column(db.String(12), nullable=False, default="IDR")
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"))
    tx_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(180), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    tx_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wallet = db.relationship("Wallet", backref="transactions")


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    monthly_limit = db.Column(db.Numeric(14, 2), nullable=False)
    spent = db.Column(db.Numeric(14, 2), nullable=False, default=0)
