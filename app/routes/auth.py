from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").lower()).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(url_for("dashboard.overview"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.overview"))
    if request.method == "POST":
        email = request.form.get("email", "").lower()
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.register"))
        user = User(name=request.form.get("name", "Rakit User"), email=email)
        user.set_password(request.form.get("password", "password"))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("dashboard.overview"))
    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("dashboard.home"))
