import os
import csv
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from io import StringIO

from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from werkzeug.security import check_password_hash, generate_password_hash

from models import Budget, Transaction, User, Wallet, db
from services import (
    CsvStatementImporter,
    DashboardService,
    FormParser,
    InvestmentProjectionCalculator,
    MarketDataService,
    TransactionRepository,
    WalletRepository,
)


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-rakit-secret")
    app.permanent_session_lifetime = timedelta(days=30)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///rakit_finance.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    if os.getenv("AUTO_INIT_DB", "1") == "1":
        with app.app_context():
            db.create_all()
            seed_demo_data()
            refresh_demo_dates()

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        seed_demo_data()
        refresh_demo_dates()
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
                session.permanent = request.form.get("remember") == "on"
                return redirect(url_for("dashboard"))
            flash("Email atau password salah.")
        return render_template("auth/login.html")

    @app.route("/auth/google-demo")
    def google_demo():
        user = User.query.filter_by(email="google.demo@rakit.local").first()
        if not user:
            user = User(
                name="Google Demo",
                email="google.demo@rakit.local",
                password_hash=generate_password_hash(os.urandom(12).hex()),
            )
            db.session.add(user)
            db.session.flush()
            create_default_wallets(user)
            db.session.commit()
        session["user_id"] = user.id
        session.permanent = True
        flash("Signed in with demo Google account.")
        return redirect(url_for("dashboard"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            agreed = request.form.get("terms") == "on"
            if not name or not email or len(password) < 8:
                flash("Lengkapi nama, email, dan password minimal 8 karakter.")
                return render_template("auth/register.html")
            if not agreed:
                flash("Kamu harus menyetujui Terms of Service dan Privacy Policy.")
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
        sent = False
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            sent = bool(email)
            if User.query.filter_by(email=email).first():
                flash("Reset link siap dikirim. Untuk demo lokal, lanjut login dengan password yang kamu buat.")
            else:
                flash("Kalau email itu terdaftar, reset link akan dikirim.")
        return render_template("auth/forgot_password.html", sent=sent)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        dashboard_service = DashboardService(user)
        wallet_repository = WalletRepository(user)
        transaction_repository = TransactionRepository(user)
        return render_template(
            "app/dashboard.html",
            active_page="dashboard",
            user=user,
            wallets=wallet_repository.options(),
            transactions=transaction_repository.recent_display_rows(),
            stats=dashboard_service.stats(),
            today=date.today().isoformat(),
        )

    @app.route("/transactions", methods=["GET", "POST"])
    @login_required
    def transactions():
        user = current_user()
        transaction_repository = TransactionRepository(user)
        wallet_repository = WalletRepository(user)
        if request.method == "POST":
            try:
                transaction_repository.create(request.form)
                flash("Transaksi berhasil disimpan.")
            except ValueError as exc:
                flash(str(exc))
            return redirect(url_for("transactions"))
        query = request.args.get("q", "").strip()
        page = max(FormParser.integer(request.args.get("page"), 1), 1)
        per_page = 5
        total = transaction_repository.count(search=query)
        total_pages = max(1, ((total - 1) // per_page) + 1) if total else 1
        page = min(page, total_pages)
        start = ((page - 1) * per_page) + 1 if total else 0
        end = min(page * per_page, total)
        return render_template(
            "app/transactions.html",
            active_page="transactions",
            user=user,
            transactions=transaction_repository.display_rows(search=query, page=page, per_page=per_page),
            wallets=wallet_repository.options(),
            query=query,
            page=page,
            total=total,
            total_pages=total_pages,
            showing_start=start,
            showing_end=end,
            today=date.today().isoformat(),
        )

    @app.post("/transactions/<int:transaction_id>/edit")
    @login_required
    def edit_transaction(transaction_id):
        try:
            TransactionRepository(current_user()).update(transaction_id, request.form)
            flash("Transaksi berhasil diperbarui.")
        except ValueError as exc:
            flash(str(exc))
        return redirect(url_for("transactions", q=request.args.get("q", ""), page=request.args.get("page", 1)))

    @app.post("/transactions/<int:transaction_id>/delete")
    @login_required
    def delete_transaction(transaction_id):
        try:
            TransactionRepository(current_user()).delete(transaction_id)
            flash("Transaksi berhasil dihapus.")
        except ValueError as exc:
            flash(str(exc))
        return redirect(url_for("transactions", q=request.args.get("q", ""), page=request.args.get("page", 1)))

    @app.route("/transactions/export")
    @login_required
    def export_transactions():
        user = current_user()
        query = request.args.get("q", "").strip()
        rows = TransactionRepository(user).export_rows(search=query)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "type", "category", "description", "wallet", "amount"])
        for tx in rows:
            writer.writerow(
                [
                    tx.tx_date.isoformat(),
                    tx.tx_type,
                    tx.category,
                    tx.description,
                    tx.wallet.name if tx.wallet else "",
                    str(tx.amount),
                ]
            )
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=rakit-transactions.csv"},
        )

    @app.route("/analytics")
    @login_required
    def analytics():
        query = request.args.get("q", "").strip()
        market_data = MarketDataService()
        return render_template(
            "app/analytics.html",
            active_page="analytics",
            user=current_user(),
            market_cards=market_data.cards(query),
            news=market_data.news(query),
            query=query,
        )

    @app.route("/investment-sim", methods=["GET", "POST"])
    @login_required
    def investment_sim():
        asset = request.form.get("asset", request.args.get("asset", "mutual_fund"))
        initial = FormParser.integer(request.form.get("initial"), 10000)
        monthly = FormParser.integer(request.form.get("monthly"), 500)
        years = FormParser.integer(request.form.get("years"), 10)
        calculator = InvestmentProjectionCalculator()
        projection = calculator.calculate(initial, monthly, years, asset_key=asset)
        return render_template(
            "app/investment.html",
            active_page="investment",
            user=current_user(),
            asset=asset,
            initial=initial,
            monthly=monthly,
            years=years,
            projection=projection,
            investment_assets=calculator.asset_metadata(),
        )

    @app.route("/accounts", methods=["GET", "POST"])
    @login_required
    def accounts():
        user = current_user()
        if request.method == "POST":
            try:
                TransactionRepository(user).create(request.form)
                flash("Transaksi berhasil disimpan.")
            except ValueError as exc:
                flash(str(exc))
            return redirect(url_for("accounts"))
        return render_template(
            "app/accounts.html",
            active_page="accounts",
            user=user,
            wallets=WalletRepository(user).display_rows(),
            today=date.today().isoformat(),
        )

    @app.post("/accounts/wallets")
    @login_required
    def add_wallet():
        try:
            WalletRepository(current_user()).create(request.form)
            flash("Wallet berhasil ditambahkan.")
        except ValueError as exc:
            flash(str(exc))
        return redirect(url_for("accounts"))

    @app.post("/accounts/wallets/<int:wallet_id>/edit")
    @login_required
    def edit_wallet(wallet_id):
        try:
            WalletRepository(current_user()).update(wallet_id, request.form)
            flash("Wallet berhasil diperbarui.")
        except ValueError as exc:
            flash(str(exc))
        return redirect(url_for("accounts"))

    @app.post("/accounts/wallets/<int:wallet_id>/delete")
    @login_required
    def delete_wallet(wallet_id):
        try:
            WalletRepository(current_user()).delete(wallet_id)
            flash("Wallet berhasil dihapus dari daftar aktif.")
        except ValueError as exc:
            flash(str(exc))
        return redirect(url_for("accounts"))

    @app.post("/accounts/import")
    @login_required
    def import_statement():
        user = current_user()
        upload = request.files.get("statement")
        try:
            imported = CsvStatementImporter(user).import_file(upload)
            flash(f"{imported} transaksi berhasil diimport.")
        except ValueError as exc:
            flash(str(exc))
        return redirect(url_for("accounts"))

    @app.post("/api/investment")
    def investment_api():
        payload = request.get_json(force=True)
        projection = InvestmentProjectionCalculator().calculate(
            FormParser.integer(payload.get("initial"), 10000),
            FormParser.integer(payload.get("monthly"), 500),
            FormParser.integer(payload.get("years"), 10),
            asset_key=payload.get("asset", "mutual_fund"),
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
    today = date.today()
    transactions = [
        ("income", "Income", "Monthly Salary", "Bank Transfer", Decimal("5000.00"), today, "BCA Account"),
        ("expense", "Food", "Starbucks Coffee", "E-Wallet", Decimal("15.50"), today - timedelta(days=1), "GoPay Wallet"),
        ("expense", "Shopping", "Amazon Purchase", "Bank Card", Decimal("89.99"), today - timedelta(days=2), "BCA Account"),
        ("expense", "Bills", "Electric Utility", "Bank Transfer", Decimal("120.00"), today - timedelta(days=3), "BCA Account"),
        ("expense", "Transport", "Uber Ride", "E-Wallet", Decimal("22.40"), today - timedelta(days=4), "GoPay Wallet"),
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


def refresh_demo_dates():
    demo_offsets = {
        "Monthly Salary": 0,
        "Starbucks Coffee": 1,
        "Amazon Purchase": 2,
        "Electric Utility": 3,
        "Uber Ride": 4,
    }
    today = date.today()
    changed = False
    for description, offset in demo_offsets.items():
        tx = Transaction.query.filter_by(description=description).first()
        if tx and tx.tx_date.year < today.year:
            tx.tx_date = today - timedelta(days=offset)
            changed = True
    if changed:
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
    default_wallet = Wallet.query.filter_by(user_id=user.id).order_by(Wallet.id).first()
    wallet_id = int(form.get("wallet_id") or default_wallet.id)
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
    tx_date = parse_date(form.get("tx_date")) or date.today()
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


def transaction_rows(user, query="", limit=10, offset=0):
    rows = (
        Transaction.query.options(joinedload(Transaction.wallet))
        .filter_by(user_id=user.id)
    )
    if query:
        like = f"%{query}%"
        rows = rows.outerjoin(Wallet).filter(
            or_(
                Transaction.category.ilike(like),
                Transaction.description.ilike(like),
                Transaction.tx_type.ilike(like),
                Wallet.name.ilike(like),
            )
        )
    rows = rows.order_by(Transaction.tx_date.desc(), Transaction.id.desc())
    if offset:
        rows = rows.offset(offset)
    if limit:
        rows = rows.limit(limit)
    return rows


def transaction_count(user, query=""):
    rows = (
        Transaction.query.options(joinedload(Transaction.wallet))
        .filter_by(user_id=user.id)
    )
    if query:
        like = f"%{query}%"
        rows = rows.outerjoin(Wallet).filter(
            or_(
                Transaction.category.ilike(like),
                Transaction.description.ilike(like),
                Transaction.tx_type.ilike(like),
                Wallet.name.ilike(like),
            )
        )
    return rows.count()


def transaction_history(user, query="", page=1, per_page=5):
    rows = transaction_rows(
        user,
        query=query,
        limit=per_page,
        offset=(page - 1) * per_page,
    ).all()
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


def safe_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_date(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


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


def investment_assets():
    return {
        "mutual_fund": {
            "label": "Mutual Fund",
            "rate": 0.085,
            "icon": "landmark",
            "description": "Diversified portfolio managed by experts",
            "outlook": "Based on current trends, Mutual Funds are expected to yield 8-12% APR over the next decade.",
        },
        "gold": {
            "label": "Gold",
            "rate": 0.055,
            "icon": "banknote",
            "description": "Safe-haven commodity for stability",
            "outlook": "Gold is modeled with steadier 4-7% APR growth and lower volatility.",
        },
        "crypto": {
            "label": "Crypto",
            "rate": 0.14,
            "icon": "bitcoin",
            "description": "High-growth digital asset volatility",
            "outlook": "Crypto projection uses higher 14% APR potential, with higher risk and volatility.",
        },
    }


def market_cards():
    return [
        ("BITCOIN (BTC/USD)", "$65,240.50", "+2.5%", "up"),
        ("ETHEREUM (ETH/USD)", "$3,512.20", "-1.2%", "down"),
        ("US 30Y TREASURY", "4.52%", "+0.05%", "up"),
        ("INDOGB 10Y BOND", "6.84%", "-0.02%", "down"),
    ]


def filter_market_cards(query):
    cards = market_cards()
    if not query:
        return cards
    needle = query.lower()
    return [card for card in cards if needle in card[0].lower()]


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


def filter_market_news(query):
    news = market_news()
    if not query:
        return news
    needle = query.lower()
    return [
        item
        for item in news
        if any(needle in str(value).lower() for value in item)
    ]


def calculate_investment_projection(initial, monthly, years, asset="mutual_fund"):
    assets = investment_assets()
    annual_rate = assets.get(asset, assets["mutual_fund"])["rate"]
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
