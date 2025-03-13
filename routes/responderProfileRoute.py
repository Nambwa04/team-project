from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from models.user import User
from services.responderService import responderService
from models.decorators import role_required
from bson import ObjectId
from datetime import datetime
from models import mongo

responderProfile_bp = Blueprint('responderProfile', __name__)

@responderProfile_bp.route('/profile')
@role_required('responder')
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
        
        # Get or create responder profile
        profile_data = mongo.db.responders.find_one({"user_id": ObjectId(user_id)})
        
        if not profile_data:
            print(f"Creating new responder profile for user: {user_id}")  # Debug log
            # Create default profile
            profile_data = {
                "user_id": ObjectId(user_id),
                "name": user.get("username", ""),
                "email": user.get("email", ""),
                "phone": "",
                "assigned_area": "",
                "availability": "Available",
                "cases_handled": 0,
                "rating": 0,
                "created_at": datetime.now()
            }
            mongo.db.responders.insert_one(profile_data)
        
        print(f"User data: {user}")  # Debug log
        print(f"Profile data: {profile_data}")  # Debug log
        
        return render_template('responder_profile.html', profile=profile_data, user=user)
    
    except Exception as e:
        print(f"Error in profile route: {str(e)}")  # Debug log
        flash("Error loading profile", "error")
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

@responderProfile_bp.route('/send_message', methods=['POST'])
@role_required('responder')
def send_message():
    try:
        user_id = session.get("user_id")
        message_content = request.form.get('message')
        
        if responderService.send_message(user_id, message_content):
            flash("Message sent successfully", "success")
        else:
            flash("Error sending message", "error")
            
        return redirect(url_for('responderProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('responderProfile.profile'))