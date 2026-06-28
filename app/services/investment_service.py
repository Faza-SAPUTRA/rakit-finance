from app.models.investment import CryptoAsset, GoldAsset, MutualFundAsset


class InvestmentService:
    assets = {
        "mutual_fund": MutualFundAsset,
        "gold": GoldAsset,
        "crypto": CryptoAsset,
    }

    @classmethod
    def project(cls, instrument: str, amount_cents: int, years: int, contribution_cents: int):
        asset_class = cls.assets.get(instrument, MutualFundAsset)
        asset = asset_class(amount_cents)
        return {
            "instrument": asset.name,
            "risk": asset.risk,
            "projection": asset.calculate_projection(years, contribution_cents),
        }

