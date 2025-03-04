from flask import Blueprint, session, render_template, redirect, url_for, flash
from models.user import User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    user = user_model.get_user_by_id(user_id)
    if user:
        user['_id'] = str(user['_id'])
        return render_template('profile.html', user=user)
    else:
        flash("User not found", "error")
        return redirect(url_for('auth.login'))

@profile_bp.route('/profile/update', methods=['POST'])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))

    update_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone')
    }
    
    if not all(update_data.values()):
        flash("All fields are required!", "error")
        return redirect(url_for('profile'))

    result = user_model.update_user(user_id, update_data)
    if result.modified_count:
        flash("Profile updated successfully!", "success")
    else:
        flash("No changes made.", "info")
    return redirect(url_for('profile'))