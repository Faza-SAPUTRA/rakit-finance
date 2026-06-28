from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.services.analytics_service import AnalyticsService


analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@analytics_bp.route("/charts")
@login_required
def charts():
    return jsonify(AnalyticsService.chart_payload(current_user))

