from datetime import datetime

from flask import Blueprint, jsonify, redirect, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.transaction import Transaction


transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


@transactions_bp.route("", methods=["GET"])
@login_required
def list_transactions():
    rows = [
        {
            "id": transaction.id,
            "merchant": transaction.merchant,
            "category": transaction.category,
            "amount": transaction.display_amount,
            "date": transaction.occurred_on.isoformat(),
            "source": transaction.source,
        }
        for transaction in current_user.transactions
    ]
    return jsonify(rows)


@transactions_bp.route("", methods=["POST"])
@login_required
def create_transaction():
    amount = int(float(request.form.get("amount", "0")) * 100)
    transaction = Transaction(
        user_id=current_user.id,
        merchant=request.form.get("merchant", "Manual Transaction"),
        category=request.form.get("category", "Uncategorized"),
        amount_cents=abs(amount),
        transaction_type=request.form.get("transaction_type", "expense"),
        source="manual",
        occurred_on=datetime.strptime(request.form.get("occurred_on"), "%Y-%m-%d").date(),
    )
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for("dashboard.transactions_page"))

