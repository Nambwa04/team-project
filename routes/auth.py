from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User, bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods =["GET", "POST"])
def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
    
            if password != confirm_password:
                flash("Passwords do not match", "danger")
                return redirect(url_for("auth.register"))
    
            if User.find_by_email(email):
                flash("Email already registered!", "danger")
                return redirect(url_for("auth.register"))
    
            User.register_user(username, email, password)
            flash("Registration Successful! Please login.", "success")
            return redirect(url_for("auth.login")) 
    
        return render_template("register.html")

@auth_bp.route("/login", methods =["GET", "POST"])

def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.find_by_email(email)

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
    
    return render_template("dashboard.html", user=user)

@auth_bp.route("/logout")
def logout():
     session.clear()
     flash("You have been logged out", "info")
     return redirect(url_for("auth.login"))