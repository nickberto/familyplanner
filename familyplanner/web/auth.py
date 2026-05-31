"""
Authentication routes and forms.
"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from familyplanner.models import User, db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    # Check if registration is enabled
    if not current_app.config.get("REGISTRATION_ENABLED", False):
        flash("Registrierung ist nicht aktiviert.", "error")
        return redirect(url_for("auth.login"))

    if current_user.is_authenticated:
        return redirect(url_for("calendar.week"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Validation
        if not username:
            flash("Benutzername ist erforderlich", "error")
            return redirect(url_for("auth.register"))

        if len(username) < 3:
            flash("Benutzername muss mindestens 3 Zeichen lang sein", "error")
            return redirect(url_for("auth.register"))

        if not password:
            flash("Passwort ist erforderlich", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Passwort muss mindestens 6 Zeichen lang sein", "error")
            return redirect(url_for("auth.register"))

        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Benutzername existiert bereits", "error")
            return redirect(url_for("auth.register"))

        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Redirect to login and show a one-time registration-success banner via query param.
        return redirect(url_for("auth.login", registered=1))

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("calendar.week"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Benutzername und Passwort sind erforderlich", "error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Dieses Konto ist inaktiv", "error")
                return redirect(url_for("auth.login"))

            login_user(user, remember=True)
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("calendar.week"))
        else:
            flash("Benutzername oder Passwort ungültig", "error")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for("auth.login"))
