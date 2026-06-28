from abc import ABC, abstractmethod
from decimal import Decimal


class InvestmentAsset(ABC):
    """Abstract investment asset. Subclasses override projection logic."""

    name = "Investment"
    risk = "medium"

    def __init__(self, principal_cents: int):
        self.principal_cents = principal_cents

    @abstractmethod
    def calculate_projection(self, years: int, contribution_cents: int) -> list[dict]:
        """Return yearly projected values in cents."""


class MutualFundAsset(InvestmentAsset):
    name = "Reksa Dana"
    risk = "balanced"

    def calculate_projection(self, years: int, contribution_cents: int) -> list[dict]:
        value = Decimal(self.principal_cents)
        rows = []
        for year in range(1, years + 1):
            value = (value + Decimal(contribution_cents * 12)) * Decimal("1.075")
            rows.append({"year": year, "value_cents": int(value)})
        return rows


class GoldAsset(InvestmentAsset):
    name = "Gold"
    risk = "steady"

    def calculate_projection(self, years: int, contribution_cents: int) -> list[dict]:
        value = Decimal(self.principal_cents)
        rows = []
        for year in range(1, years + 1):
            value = value * Decimal("1.045") + Decimal(contribution_cents * 12)
            rows.append({"year": year, "value_cents": int(value)})
        return rows


class CryptoAsset(InvestmentAsset):
    name = "Crypto"
    risk = "high"

    def calculate_projection(self, years: int, contribution_cents: int) -> list[dict]:
        value = Decimal(self.principal_cents)
        rows = []
        for year in range(1, years + 1):
            cycle_rate = Decimal("1.22") if year % 4 != 0 else Decimal("0.82")
            value = (value + Decimal(contribution_cents * 12)) * cycle_rate
            rows.append({"year": year, "value_cents": int(max(value, Decimal(0)))})
        return rows

