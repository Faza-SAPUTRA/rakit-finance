from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models.transaction import Transaction
from app.services.ocr_service import OCRService


receipt_bp = Blueprint("receipt", __name__, url_prefix="/api/receipt")


@receipt_bp.route("/scan", methods=["POST"])
@login_required
def scan_receipt():
    file_storage = request.files.get("receipt")
    if not file_storage:
        return jsonify({"error": "No receipt uploaded."}), 400
    try:
        result = OCRService().extract_receipt(file_storage)
    except Exception:
        result = {
            "merchant": "Manual Receipt",
            "amount_cents": 0,
            "occurred_on": datetime.utcnow().date().isoformat(),
            "raw_text": "OCR engine unavailable. Enter receipt details manually.",
        }
    return jsonify(result)


@receipt_bp.route("/save", methods=["POST"])
@login_required
def save_receipt():
    data = request.get_json(silent=True) or {}
    tx = Transaction(
        user_id=current_user.id,
        merchant=data.get("merchant", "Receipt"),
        category=data.get("category", "Receipts"),
        amount_cents=int(data.get("amount_cents", 0)),
        transaction_type="expense",
        source="ocr",
        occurred_on=datetime.strptime(data.get("occurred_on"), "%Y-%m-%d").date(),
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"id": tx.id, "message": "Receipt saved"})

