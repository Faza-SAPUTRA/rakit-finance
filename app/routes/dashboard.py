from flask import Blueprint, render_template
from flask.views import MethodView
from flask_login import current_user, login_required

from app.services.analytics_service import AnalyticsService


dashboard_bp = Blueprint("dashboard", __name__)
landing_bp = Blueprint("landing", __name__)


@dashboard_bp.app_template_filter("rupiah")
def rupiah(value):
    return f"Rp {int(value or 0) / 100:,.0f}"


@dashboard_bp.app_context_processor
def utility_processor():
    return {"rupiah": rupiah}


@landing_bp.route("/")
def home():
    return render_template("landing/index.html")


@landing_bp.route("/features")
def features():
    return render_template("landing/features.html")


@landing_bp.route("/how-it-works")
def how_it_works():
    return render_template("landing/how_it_works.html")


@landing_bp.route("/why-rakit")
def why_rakit():
    return render_template("landing/why_rakit.html")


@landing_bp.route("/pricing")
def pricing():
    return render_template("landing/pricing.html")


class OverviewView(MethodView):
    decorators = [login_required]

    def get(self):
        summary = AnalyticsService.dashboard_summary(current_user)
        transactions = current_user.transactions[:8]
        return render_template("dashboard/overview.html", summary=summary, transactions=transactions)


@dashboard_bp.route("/transactions")
@login_required
def transactions_page():
    transactions = current_user.transactions
    return render_template("dashboard/transactions.html", transactions=transactions)


@dashboard_bp.route("/smart-import")
@login_required
def smart_import():
    return render_template("dashboard/smart_import.html")


@dashboard_bp.route("/receipt-scanner")
@login_required
def receipt_scanner():
    return render_template("dashboard/receipt_scanner.html")


@dashboard_bp.route("/assets-liabilities")
@login_required
def assets_liabilities():
    return render_template("dashboard/assets_liabilities.html", accounts=current_user.accounts)


@dashboard_bp.route("/investment-simulator")
@login_required
def investment_simulator():
    return render_template("dashboard/investment_simulator.html")


@dashboard_bp.route("/market-analytics")
@login_required
def market_analytics():
    return render_template("dashboard/market_analytics.html", news=AnalyticsService.market_news())


@dashboard_bp.route("/settings")
@login_required
def settings():
    return render_template("dashboard/settings.html")


dashboard_bp.add_url_rule("/dashboard", view_func=OverviewView.as_view("overview"))
