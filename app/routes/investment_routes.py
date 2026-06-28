from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.services.investment_service import InvestmentService


investment_bp = Blueprint("investment", __name__, url_prefix="/api/investment")


@investment_bp.route("/project", methods=["POST"])
@login_required
def project():
    data = request.get_json(silent=True) or request.form
    amount_cents = int(float(data.get("amount", 0)) * 100)
    contribution_cents = int(float(data.get("contribution", 0)) * 100)
    years = max(1, min(30, int(data.get("years", 5))))
    return jsonify(InvestmentService.project(data.get("instrument", "mutual_fund"), amount_cents, years, contribution_cents))

