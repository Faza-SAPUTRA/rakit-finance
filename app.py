import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from models import Budget, Transaction, User, Wallet, db


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-rakit-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///rakit_finance.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    if os.getenv("AUTO_INIT_DB", "1") == "1":
        with app.app_context():
            db.create_all()
            seed_demo_data()

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        seed_demo_data()
        print("Database tables and demo data are ready.")

    @app.route("/")
    def index():
        if current_user():
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                session["user_id"] = user.id
                return redirect(url_for("dashboard"))
            flash("Email atau password salah.")
        return render_template("auth/login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not name or not email or len(password) < 8:
                flash("Lengkapi nama, email, dan password minimal 8 karakter.")
                return render_template("auth/register.html")
            if User.query.filter_by(email=email).first():
                flash("Email sudah terdaftar. Silakan sign in.")
                return redirect(url_for("login"))
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.flush()
            create_default_wallets(user)
            db.session.commit()
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        return render_template("auth/register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        sent = request.method == "POST"
        return render_template("auth/forgot_password.html", sent=sent)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        return render_template(
            "app/dashboard.html",
            active_page="dashboard",
            user=user,
            wallets=wallet_options(user),
            transactions=recent_transactions(user),
            stats=dashboard_stats(user),
        )

    @app.route("/transactions", methods=["GET", "POST"])
    @login_required
    def transactions():
        user = current_user()
        if request.method == "POST":
            create_transaction_from_form(user, request.form)
            return redirect(url_for("transactions"))
        return render_template(
            "app/transactions.html",
            active_page="transactions",
            user=user,
            transactions=transaction_history(user),
        )

    @app.route("/analytics")
    @login_required
    def analytics():
        return render_template(
            "app/analytics.html",
            active_page="analytics",
            user=current_user(),
            market_cards=market_cards(),
            news=market_news(),
        )

    @app.route("/investment-sim", methods=["GET", "POST"])
    @login_required
    def investment_sim():
        initial = int(request.form.get("initial", 10000))
        monthly = int(request.form.get("monthly", 500))
        years = int(request.form.get("years", 10))
        projection = calculate_investment_projection(initial, monthly, years)
        return render_template(
            "app/investment.html",
            active_page="investment",
            user=current_user(),
            initial=initial,
            monthly=monthly,
            years=years,
            projection=projection,
        )

    @app.route("/accounts", methods=["GET", "POST"])
    @login_required
    def accounts():
        user = current_user()
        if request.method == "POST":
            create_transaction_from_form(user, request.form)
            return redirect(url_for("accounts"))
        return render_template(
            "app/accounts.html",
            active_page="accounts",
            user=user,
            wallets=wallets(user),
        )

    @app.post("/api/investment")
    def investment_api():
        payload = request.get_json(force=True)
        projection = calculate_investment_projection(
            int(payload.get("initial", 10000)),
            int(payload.get("monthly", 500)),
            int(payload.get("years", 10)),
        )
        return jsonify(projection)

    @app.template_filter("money")
    def money(value):
        return "${:,.2f}".format(float(value))

    @app.template_filter("idr")
    def idr(value):
        return "IDR {:,.0f}".format(float(value))

    return app


def login_required(view):
    def wrapped_view(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    wrapped_view.__name__ = view.__name__
    return wrapped_view


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def seed_demo_data():
    if User.query.first():
        return
    user = User(
        name="Alex Morgan",
        email="alex@example.com",
        password_hash=generate_password_hash("password"),
    )
    db.session.add(user)
    db.session.flush()
    create_default_wallets(user)
    db.session.flush()
    wallets_by_name = {wallet.name: wallet for wallet in user.wallets}
    transactions = [
        ("income", "Income", "Monthly Salary", "Bank Transfer", Decimal("5000.00"), date(2023, 10, 14), "BCA Account"),
        ("expense", "Food", "Starbucks Coffee", "E-Wallet", Decimal("15.50"), date(2023, 10, 13), "GoPay Wallet"),
        ("expense", "Shopping", "Amazon Purchase", "Bank Card", Decimal("89.99"), date(2023, 10, 12), "BCA Account"),
        ("expense", "Bills", "Electric Utility", "Bank Transfer", Decimal("120.00"), date(2023, 10, 12), "BCA Account"),
        ("expense", "Transport", "Uber Ride", "E-Wallet", Decimal("22.40"), date(2023, 10, 11), "GoPay Wallet"),
    ]
    for tx_type, category, description, account, amount, tx_date, wallet_name in transactions:
        db.session.add(
            Transaction(
                user_id=user.id,
                wallet_id=wallets_by_name[wallet_name].id,
                tx_type=tx_type,
                category=category,
                description=description,
                amount=amount,
                tx_date=tx_date,
            )
        )
    db.session.add(Budget(user_id=user.id, category="Food", monthly_limit=Decimal("450.00"), spent=Decimal("15.50")))
    db.session.commit()


def create_default_wallets(user):
    db.session.add_all(
        [
            Wallet(user_id=user.id, name="BCA Account", wallet_type="bank", balance=Decimal("15250.00"), currency="USD"),
            Wallet(user_id=user.id, name="GoPay Wallet", wallet_type="ewallet", balance=Decimal("1420.00"), currency="USD"),
            Wallet(user_id=user.id, name="OVO", wallet_type="ewallet", balance=Decimal("850.00"), currency="USD"),
        ]
    )


def create_transaction_from_form(user, form):
    wallet_id = int(form.get("wallet_id") or user.wallets[0].id)
    wallet = Wallet.query.filter_by(id=wallet_id, user_id=user.id).first_or_404()
    tx_type = form.get("tx_type", "expense")
    try:
        amount = Decimal(str(form.get("amount", "0")).replace(",", ""))
    except InvalidOperation:
        flash("Amount tidak valid.")
        return
    if amount < 0:
        amount = abs(amount)
    if amount == 0:
        flash("Amount harus lebih dari 0.")
        return
    tx_date_raw = form.get("tx_date") or date.today().isoformat()
    tx_date = datetime.strptime(tx_date_raw, "%Y-%m-%d").date()
    transaction = Transaction(
        user_id=user.id,
        wallet_id=wallet.id,
        tx_type=tx_type,
        category=form.get("category", "General"),
        description=form.get("description") or "Manual transaction",
        amount=amount,
        tx_date=tx_date,
    )
    if tx_type == "income":
        wallet.balance += amount
    else:
        wallet.balance -= amount
    db.session.add(transaction)
    db.session.commit()
    flash("Transaksi berhasil disimpan.")


def dashboard_stats(user):
    total_balance = db.session.query(func.coalesce(func.sum(Wallet.balance), 0)).filter_by(user_id=user.id).scalar()
    total_income = transaction_sum(user, "income")
    total_expense = transaction_sum(user, "expense")
    return [
        {
            "label": "Total Balance",
            "value": money_value(total_balance),
            "trend": "2.4%",
            "tone": "green",
            "icon": "landmark",
        },
        {
            "label": "Monthly Income",
            "value": money_value(total_income),
            "trend": "1.2%",
            "tone": "blue",
            "icon": "trending-down",
        },
        {
            "label": "Monthly Expense",
            "value": money_value(total_expense),
            "trend": "5.0%",
            "tone": "orange",
            "icon": "shopping-cart",
        },
    ]


def transaction_sum(user, tx_type):
    return (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter_by(user_id=user.id, tx_type=tx_type)
        .scalar()
    )


def recent_transactions(user):
    rows = (
        Transaction.query.filter_by(user_id=user.id)
        .order_by(Transaction.tx_date.desc(), Transaction.id.desc())
        .limit(3)
        .all()
    )
    return [
        (
            category_icon(tx.category, tx.tx_type),
            tx.description,
            tx.category,
            tx.tx_date.strftime("%b %d, %Y"),
            signed_money(tx),
            "in" if tx.tx_type == "income" else "out",
        )
        for tx in rows
    ]


def transaction_history(user):
    rows = (
        Transaction.query.filter_by(user_id=user.id)
        .order_by(Transaction.tx_date.desc(), Transaction.id.desc())
        .limit(10)
        .all()
    )
    return [
        (
            tx.tx_date.strftime("%b %d, %Y"),
            tx.category,
            tx.description,
            tx.wallet.name if tx.wallet else "Wallet",
            signed_money(tx),
            "in" if tx.tx_type == "income" else "out",
        )
        for tx in rows
    ]


def wallets(user):
    tone_by_type = {"bank": "blue", "ewallet": "teal"}
    icon_by_type = {"bank": "landmark", "ewallet": "wallet"}
    rows = Wallet.query.filter_by(user_id=user.id).order_by(Wallet.id).all()
    return [
        (
            icon_by_type.get(wallet.wallet_type, "wallet"),
            wallet.name,
            wallet.balance,
            tone_by_type.get(wallet.wallet_type, "purple"),
            wallet.id,
        )
        for wallet in rows
    ]


def wallet_options(user):
    return Wallet.query.filter_by(user_id=user.id).order_by(Wallet.id).all()


def money_value(value):
    return "${:,.2f}".format(float(value or 0))


def signed_money(transaction):
    sign = "+" if transaction.tx_type == "income" else "-"
    return f"{sign}{money_value(transaction.amount)}"


def category_icon(category, tx_type):
    if tx_type == "income":
        return "briefcase"
    icons = {
        "Shopping": "shopping-bag",
        "Food": "utensils",
        "Food & Drink": "utensils",
        "Bills": "receipt-text",
        "Transport": "car",
    }
    return icons.get(category, "wallet")


def market_cards():
    return [
        ("BITCOIN (BTC/USD)", "$65,240.50", "+2.5%", "up"),
        ("ETHEREUM (ETH/USD)", "$3,512.20", "-1.2%", "down"),
        ("US 30Y TREASURY", "4.52%", "+0.05%", "up"),
        ("INDOGB 10Y BOND", "6.84%", "-0.02%", "down"),
    ]


def market_news():
    return [
        (
            "CNBC",
            "2 hours ago",
            "Global Markets React to Fed Policy Shift and Inflation Targets",
            "Investors are pivoting as treasury yields fluctuate following the latest central bank announcement regarding long-term inflation targets and potential rate adjustments.",
        ),
        (
            "FINANCIALJUICE",
            "4 hours ago",
            "Oil Prices Surge Amidst Tensions in Key Transit Corridors",
            "Energy markets are on high alert as diplomatic escalations threaten major supply routes. Crude futures rose by 1.5% in early morning trading.",
        ),
        (
            "CNBC",
            "5 hours ago",
            "European Tech Stocks Hit 52-Week High as Sector Sentiment Improves",
            "Renewed interest in semiconductor manufacturing and AI software development has propelled several major European tech conglomerates to record heights this quarter.",
        ),
    ]


def calculate_investment_projection(initial, monthly, years):
    annual_rate = 0.085
    balance = float(initial)
    rows = []
    labels = []
    balances = []
    total_contribution = float(initial)
    total_interest = 0.0

    for year in range(1, years + 1):
        annual_contribution = monthly * 12
        balance += annual_contribution
        interest = balance * annual_rate
        balance += interest
        total_contribution += annual_contribution
        total_interest += interest
        labels.append(str(date.today().year + year - 1))
        balances.append(round(balance, 2))
        rows.append(
            {
                "year": f"Year {year}",
                "contribution": annual_contribution,
                "interest": round(interest, 2),
                "balance": round(balance, 2),
            }
        )

    return {
        "labels": labels,
        "balances": balances,
        "total_contribution": round(total_contribution, 2),
        "interest_earned": round(total_interest, 2),
        "estimated_total": round(balance, 2),
        "rows": rows[:5],
    }


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
