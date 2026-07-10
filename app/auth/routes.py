from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # ---- Validierung (Geschaeftslogik) ----
        errors = []
        if len(username) < 3:
            errors.append("Benutzername muss mind. 3 Zeichen lang sein.")
        if "@" not in email or "." not in email:
            errors.append("Bitte eine gueltige E-Mail-Adresse angeben.")
        if len(password) < 6:
            errors.append("Passwort muss mind. 6 Zeichen lang sein.")
        if User.query.filter_by(username=username).first():
            errors.append("Dieser Benutzername ist bereits vergeben.")
        if User.query.filter_by(email=email).first():
            errors.append("Diese E-Mail-Adresse ist bereits registriert.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html")

        # Der allererste registrierte User im System wird automatisch Admin,
        # damit ohne manuelle DB-Bearbeitung ein Adminkonto existiert.
        is_first_user = User.query.count() == 0
        user = User(username=username, email=email, role="admin" if is_first_user else "user")
        user.set_password(password)
        if is_first_user:
            user.generate_api_token()

        db.session.add(user)
        db.session.commit()

        flash("Registrierung erfolgreich. Du kannst dich jetzt einloggen.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Willkommen zurueck, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Benutzername oder Passwort ist falsch.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Du wurdest ausgeloggt.", "info")
    return redirect(url_for("main.index"))
