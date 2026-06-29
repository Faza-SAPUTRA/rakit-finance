# Rakit Finance

Flask-based expense tracker UI sliced from the provided `ui/` mockups.

## Run locally

```powershell
py -m pip install -r requirements.txt
copy .env.example .env
py -m flask --app app run --debug
```

Open `http://127.0.0.1:5000/login`.

Demo login:

```text
Email: alex@example.com
Password: password
```

## MySQL setup

Update `.env`:

```env
DATABASE_URL=mysql+pymysql://rakit_user:rakit_password@localhost:3306/rakit_finance
```

Auth, dashboard stats, wallets, and transactions are backed by SQLAlchemy models in `models.py`. Market analytics content is still static demo content for the sliced UI.

Tables and demo data are created automatically while `AUTO_INIT_DB=1`. You can also run it manually:

```powershell
py -m flask --app app init-db
```
