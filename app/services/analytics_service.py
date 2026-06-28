from collections import Counter


class AnalyticsService:
    @staticmethod
    def dashboard_summary(user):
        assets = sum(account.net_worth_contribution() for account in user.accounts if account.account_type == "asset")
        liabilities = -sum(
            account.net_worth_contribution() for account in user.accounts if account.account_type == "liability"
        )
        net_worth = assets - liabilities
        spend_by_category = Counter()
        for transaction in user.transactions:
            if transaction.transaction_type == "expense":
                spend_by_category[transaction.category] += transaction.amount_cents
        return {
            "assets_cents": assets,
            "liabilities_cents": liabilities,
            "net_worth_cents": net_worth,
            "spend_categories": spend_by_category,
            "risk_index": AnalyticsService.risk_index(user),
        }

    @staticmethod
    def chart_payload(user):
        summary = AnalyticsService.dashboard_summary(user)
        categories = summary["spend_categories"] or {"Food": 42000000, "Transport": 18000000, "Bills": 22000000}
        total_assets = max(summary["assets_cents"], 1)
        liability_ratio = min(summary["liabilities_cents"] / total_assets, 1)
        return {
            "portfolio": {
                "labels": ["Cash", "Investments", "Emergency Fund"],
                "values": [42, 38, 20],
            },
            "spending": {
                "labels": list(categories.keys()),
                "values": [round(value / 100) for value in categories.values()],
            },
            "risk": {
                "score": summary["risk_index"],
                "liability_ratio": round(liability_ratio * 100, 1),
            },
            "news": AnalyticsService.market_news(),
        }

    @staticmethod
    def risk_index(user) -> int:
        assets = sum(account.balance_cents for account in user.accounts if account.account_type == "asset")
        liabilities = sum(account.balance_cents for account in user.accounts if account.account_type == "liability")
        if assets <= 0:
            return 72
        return min(95, int((liabilities / assets) * 100) + 18)

    @staticmethod
    def market_news():
        return [
            {"title": "IHSG opens stronger as financial stocks recover", "tag": "Market"},
            {"title": "Gold consolidates after weekly inflow to safe haven assets", "tag": "Gold"},
            {"title": "Crypto majors trade sideways while volatility cools", "tag": "Crypto"},
            {"title": "Money-market funds remain popular for emergency reserves", "tag": "Funds"},
        ]

