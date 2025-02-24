from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User, bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    print(request.form)  # Debugging: Check if data is received
    if request.method == "POST":
        # Get form data
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("auth.register"))

        # Check if email is already registered
        if User.find_by_email(email):
            flash("Email already registered!", "danger")
            return redirect(url_for("auth.register"))

        # Register the user
        User.register_user(username, email, password)
        flash("Registration Successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get form data
        email = request.form["email"]
        password = request.form["password"]

        # Find user by email
        user = User.find_by_email(email)

        # Check if user exists and password is correct
        if user and bcrypt.check_password_hash(user["password"], password):
            session["email"] = email
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/dashboard")
def dashboard():
    # Check if user is logged in
    if "email" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    # Get current user's information
    user = User.find_by_email(session["email"])

    # Example initial data for the dashboard chart (Modify as needed)
    initial_data = {
        "labels": ["January", "February", "March"],
        "values": [10, 20, 30]
    }

    # Pass initial_data to the template
    return render_template("responders.html", user=user, initial_data=initial_data)

@auth_bp.route("/logout")
def logout():
    # Clear the session
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))