# Rakit Finance

Flask-based expense tracker sliced from the provided `ui/` mockups. The app uses Flask, Jinja templates, vanilla JavaScript, Chart.js, SQLAlchemy, and MySQL through PyMySQL.

## Current Structure

```text
app.py                 Flask routes, auth flow, request handling, and response rendering
models.py              SQLAlchemy models for users, wallets, transactions, and budgets
services.py            OOP service/repository layer for CRUD, calculations, import, and investment projections
requirements.txt       Python dependencies
static/css/app.css     Application styling
static/js/app.js       UI interactions and Chart.js setup
templates/auth/        Sign in, register, and forgot password pages
templates/app/         Dashboard, transactions, analytics, accounts, investment pages
ui/                    Reference mockup images
```

The project is currently a flat Flask app with a separate OOP service layer. Flask routes stay in `app.py`, database models stay in `models.py`, and business logic lives in `services.py`.

## Data Model

The real SQLAlchemy classes live in `models.py`:

- `User`: account identity and authentication ownership.
- `Wallet`: bank or e-wallet balance owned by a user.
- `Transaction`: income or expense records linked to a wallet.
- `Budget`: simple category budget data for dashboard demos.

Investment projection logic lives in `services.py` as asset strategy classes, while submitted form/API values are handled through Flask routes in `app.py`.

## Service Layer

The main backend behavior is implemented with Python classes in `services.py`:

- `WalletRepository`: create, read, update, and archive/delete wallets per user.
- `TransactionRepository`: create, read, update, delete, search, paginate, and export transactions per user.
- `DashboardService`: computes user-specific balance, income, and expense metrics.
- `CsvStatementImporter`: imports CSV statement rows into user-owned transactions.
- `InvestmentProjectionCalculator`: delegates projection math to asset classes.
- `MutualFundAsset`, `GoldAsset`, `CryptoAsset`: OOP investment strategies with their own projection behavior.

Every wallet and transaction query is scoped by `user_id`, so users only operate on their own MySQL-backed data.

## Receipt Scanner Status

The Smart Receipt Scanner on the Transactions page is currently a UI demo preview. Uploading a receipt updates the scanner result with placeholder preview values so the confirmation workflow can be demonstrated.

It does not run OCR, Tesseract, or image parsing yet.

## Run Locally

```powershell
py -m pip install -r requirements.txt
```

Create a local `.env` file:

```env
SECRET_KEY=dev-rakit-secret
AUTO_INIT_DB=1
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/rakit_finance
```

Start Flask:

```powershell
py -m flask --app app run --debug
```

Open `http://127.0.0.1:5000/login`.

Demo login:

```text
Email: alex@example.com
Password: password
```

## Database Setup

With XAMPP/MySQL running, create a database named `rakit_finance`, then use the `DATABASE_URL` value above or adjust the username/password for your local MySQL setup.

Tables and demo data are created automatically while `AUTO_INIT_DB=1`. You can also run setup manually:

```powershell
py -m flask --app app init-db
```

Auth, dashboard stats, wallets, transactions, CSV import, and CSV export are backed by SQLAlchemy. Market analytics/news content remains static demo content for the sliced UI.
