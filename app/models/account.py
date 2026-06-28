from abc import ABC, ABCMeta, abstractmethod
from decimal import Decimal

from app.extensions import db


class SQLAlchemyABCMeta(type(db.Model), ABCMeta):
    """Lets SQLAlchemy models also enforce abc.ABC abstract methods."""


class Account(db.Model, ABC, metaclass=SQLAlchemyABCMeta):
    """Abstract account base class used by AssetAccount and LiabilityAccount."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    balance_cents = db.Column(db.Integer, nullable=False, default=0)
    account_type = db.Column(db.String(50), nullable=False)
    institution = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="accounts")

    __mapper_args__ = {
        "polymorphic_on": account_type,
        "polymorphic_identity": "account",
    }

    @property
    def balance(self) -> Decimal:
        return Decimal(self.balance_cents) / Decimal(100)

    @balance.setter
    def balance(self, value):
        self.balance_cents = int(Decimal(str(value)) * 100)

    def display_balance(self) -> str:
        return f"Rp {self.balance_cents / 100:,.0f}"

    @abstractmethod
    def net_worth_contribution(self) -> int:
        """Return signed cents contributed to net worth."""

    @abstractmethod
    def apply_delta(self, amount_cents: int) -> None:
        """Apply a signed change to the stored balance."""


class AssetAccount(Account):
    __mapper_args__ = {"polymorphic_identity": "asset"}

    def net_worth_contribution(self) -> int:
        return self.balance_cents

    def apply_delta(self, amount_cents: int) -> None:
        self.balance_cents += amount_cents


class LiabilityAccount(Account):
    __mapper_args__ = {"polymorphic_identity": "liability"}

    def net_worth_contribution(self) -> int:
        return -self.balance_cents

    def apply_delta(self, amount_cents: int) -> None:
        self.balance_cents += amount_cents


def transfer(amount_cents: int, from_account: Account, to_account: Account) -> None:
    """Transfer between any account subtype through the Account interface."""

    if amount_cents <= 0:
        raise ValueError("Transfer amount must be positive.")
    from_account.apply_delta(-amount_cents)
    to_account.apply_delta(amount_cents)

