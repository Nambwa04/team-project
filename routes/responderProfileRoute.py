from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from models.user import User
from services import ResponderService
from models.decorators import role_required
from bson import ObjectId

responderProfile_bp = Blueprint('responderProfile', __name__)
responderService = ResponderService()

@responderProfile_bp.route('/profile')
@role_required('responder')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    profile_data = responderService.get_responder_profile(user_id)
    if profile_data:
        return render_template('responder_profile.html', profile=profile_data)
    else:
        flash("Profile not found", "error")
        return redirect(url_for('auth.login'))

@responderProfile_bp.route('/profile/update', methods=['POST'])
@role_required('responder')
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))

    user_update = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'contact': request.form.get('contact')
    }

    responder_update = {
        'specialization': request.form.get('specialization'),
        'location': request.form.get('location'),
        'availability': request.form.get('availability'),
        'experience_years': request.form.get('experience_years')
    }
    
    try:
        # Update user model data
        User.collection.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": user_update}
        )

        # Update responder-specific data
        responderService.responders.update_one(
            {"user_id": ObjectId(user_id)}, 
            {"$set": responder_update}
        )

        flash("Profile updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating profile: {str(e)}", "error")
    
    return redirect(url_for('responderProfile.profile'))