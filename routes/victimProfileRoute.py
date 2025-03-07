from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from models.user import User
from services.victimService import VictimService
from models.decorators import role_required
from bson import ObjectId

victimProfile_bp = Blueprint('victimProfile', __name__)
victimService = VictimService()

@victimProfile_bp.route('/profile')
@role_required('victim')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    profile_data = victimService.get_victim_profile(user_id)
    if profile_data:
        return render_template('victim_profile.html', profile=profile_data)
    else:
        flash("Profile not found", "error")
        return redirect(url_for('auth.login'))

@victimProfile_bp.route('/profile/update', methods=['POST'])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))

    user_update = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone')
    }

    victim_update = {
        'location': request.form.get('location'),
        'case_description': request.form.get('case_description')
    }
    
    # using user model for updates
    User.collection.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": user_update}
    )

    victimService.victims.update_one(
        {"user_id": ObjectId(user_id)}, 
        {"$set": victim_update}
    )

    if user_update or victim_update:
        flash("Profile updated successfully!", "success")
    else:
        flash("No changes made.", "info")
    return redirect(url_for('victimProfile.profile'))