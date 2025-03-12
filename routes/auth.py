from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User, bcrypt
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from services.victimService import victimService
from utils import generate_reset_token, send_reset_email, verify_reset_token

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

        # Checking if user exists
        if User.find_by_email(email):
            flash("Email already exists", "danger")
            return redirect(url_for("auth.register"))

        try:
            # Create new user
            user = User.register_user(username, email, password, role="victim")
            user_id = user.inserted_id  # Ensure correct user_id retrieval
            
            print("Newly Registered User ID:", user_id)  # Debugging line

            # Create victim profile
            victimService.victims.insert_one({
                "user_id": user_id,
                "username": username,
                "email": email,
                "phone": phone,
                "location": location,
                "gender": gender,
                "case_description": "Unknown"
            })

            print(request.form)  # Debugging line

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

        if not user:
            print("User not found")  # Debugging line
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        if not User.verify_password(user, password):
            print("Password does not match")  # Debugging line
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        # Store user details in session
        session["user_id"] = str(user["_id"])
        session["username"] = user["username"]
        session["email"] = email
        session["role"] = user["role"].lower()  # Store lowercase role in session

        print("User Role Stored in Session:", session["role"])  # Debugging line

        # Redirect based on role
        role = session["role"]
        if role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif role == "responder":
            return redirect(url_for("responder.dashboard"))
        elif role == "organization":
            return redirect(url_for("organization.dashboard"))
        elif role == "victim":
            return redirect(url_for("victim.dashboard"))

        flash("Invalid role assigned to user", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return render_template("frontpage.html")

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
        else:
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
            # Pass the plain password to update_password
            User.update_password(user['_id'], new_password)
            flash("Your password has been reset successfully.", "success")
            return redirect(url_for('auth.login'))
        flash("User not found.", "error")
    return render_template('reset_password.html', token=token)
