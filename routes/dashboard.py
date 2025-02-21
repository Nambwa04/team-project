from flask import Blueprint, session, redirect, url_for, flash

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" in session:
        return f"welcome {session['username']}! <a href = '{url_for('auth.logout')}'>Logout</a>"
    flash("Please login first", "warning")
    return redirect(url_for("auth.login"))