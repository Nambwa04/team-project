from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User, bcrypt
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from services.victimService import victimService
from utils import generate_reset_token, send_reset_email, verify_reset_token
# from services.authService import AuthService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        location = request.form["location"]
        gender = request.form["gender"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Checking if user  exists
        if User.find_by_email(email):
            flash("Email already exists", "danger")
            return redirect(url_for("auth.register"))

        try:
            #create new user
            user_id = User.register_user(username, email, password, role="victim").inserted_id

            #create victim profile
            victimService.victims.insert_one({
                "user_id": user_id,
                "username": username,
                "email": email,
                "phone": phone,
                "location": location,
                "gender": gender,
                "case_description": "Unknown"
            })

            flash("Account created successfully", "success")
            return redirect(url_for("auth.login"))

        except DuplicateKeyError:
            flash("Username or Email already exists", "danger")
            return redirect(url_for("auth.register"))
    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.find_by_email(email)

        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            session["email"] = email
            session["role"] = user["role"]  # Store role in session
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/dashboard")
def dashboard():
    if "email" not in session:
        flash("Please login first", "warning")
        return redirect(url_for("auth.login"))

    user = User.find_by_email(session["email"])
    role = session.get("role", "victim")

    # Get victim profile if role is victim
    profile = None
    if role == "victim":
        profile = victimService.get_victim_profile(user["_id"])

    # Redirect based on role
    if role == 'admin':
        return render_template('admin.html', user=user)
    elif role == 'responder':
        return render_template('responder_profile.html', user=user)
    elif role == 'organization':
        return render_template('organization_profile.html', user=user)
    else: 
        return render_template('victim_profile.html', user=user, profile=profile)

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.find_by_email(email)
        if user:
            # Generate a password reset token
            reset_token = generate_reset_token(user['email'])
            # Send the reset email
            send_reset_email(user['email'], reset_token)
            flash("Password reset link sent to your email.", "success")

            return redirect(url_for('auth.login'))
            flash("Email not found", "error")
    return render_template('forgot_password.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token')
    if not token:
        flash("Invalid or missing token.", "error")
        return redirect(url_for('auth.forgot_password'))

    email = verify_reset_token(token)
    if not email:
        flash("Invalid or expired token.", "error")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('reset_password.html', token=token)

        # Update the user's password
        user = User.find_by_email(email)
        if user:
            User.update_password(user['_id'], new_password)
            flash("Your password has been reset successfully.", "success")
            return redirect(url_for('auth.login'))
        flash("User not found.", "error")
    return render_template('reset_password.html', token=token)