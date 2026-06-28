from app.extensions import db


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=True)
    merchant = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="Uncategorized")
    amount_cents = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False, default="expense")
    source = db.Column(db.String(80), nullable=False, default="manual")
    occurred_on = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="transactions")
    account = db.relationship("Account")

    @property
    def signed_amount_cents(self) -> int:
        return self.amount_cents if self.transaction_type == "income" else -self.amount_cents

    @property
    def display_amount(self) -> str:
        sign = "+" if self.transaction_type == "income" else "-"
        return f"{sign}Rp {self.amount_cents / 100:,.0f}"

