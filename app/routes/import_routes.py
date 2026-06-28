from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime

from app.extensions import db
from app.services.import_service import ImportService


import_bp = Blueprint("import", __name__, url_prefix="/api/import")


@import_bp.route("/preview", methods=["POST"])
@login_required
def preview_import():
    source = request.form.get("source", "bca")
    file_storage = request.files.get("file")
    if not file_storage:
        return jsonify({"error": "No file uploaded."}), 400
    try:
        transactions = ImportService.parse(source, file_storage, current_user.id)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "transactions": [
                {
                    "merchant": tx.merchant,
                    "category": tx.category,
                    "amount_cents": tx.amount_cents,
                    "transaction_type": tx.transaction_type,
                    "source": tx.source,
                    "occurred_on": tx.occurred_on.isoformat(),
                }
                for tx in transactions
            ]
        }
    )


@import_bp.route("/confirm", methods=["POST"])
@login_required
def confirm_import():
    rows = request.get_json(silent=True) or {}
    created = 0
    from app.models.transaction import Transaction

    for row in rows.get("transactions", []):
        tx = Transaction(
            user_id=current_user.id,
            merchant=row.get("merchant", "Imported Transaction"),
            category=row.get("category", "Imported"),
            amount_cents=int(row.get("amount_cents", 0)),
            transaction_type=row.get("transaction_type", "expense"),
            source=row.get("source", "manual"),
            occurred_on=datetime.strptime(row.get("occurred_on"), "%Y-%m-%d").date(),
        )
        db.session.add(tx)
        created += 1
    db.session.commit()
    return jsonify({"created": created})
