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
    try:
        user_id = session.get("user_id")
        if not user_id:
            flash("You need to login first", "error")
            return redirect(url_for('auth.login'))
        
        print(f"Looking up profile for user_id: {user_id}")  # Debug log
        
        # Get user data
        user = User.find_by_id(ObjectId(user_id))
        if not user:
            print(f"User not found for ID: {user_id}")  # Debug log
            flash("User not found", "error")
            return redirect(url_for('auth.login'))
        
        # Get or create victim profile
        profile_data = victimService.get_victim_profile(user_id)
        
        print(f"User data: {user}")  # Debug log
        print(f"Profile data: {profile_data}")  # Debug log
        
        if profile_data:
            return render_template('victim_profile.html', profile=profile_data, user=user)
        else:
            flash("Error loading profile", "error")
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        print(f"Error in profile route: {str(e)}")  # Debug log
        flash("Error loading profile", "error")
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