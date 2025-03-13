from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from models.user import User
from services.victimService import victimService
from models.decorators import role_required
from bson import ObjectId
from datetime import datetime

victimProfile_bp = Blueprint('victimProfile', __name__)

@victimProfile_bp.route('/profile')
@role_required('victim')
def profile():
    try:
        user_id = session.get("user_id")
        if not user_id:
            flash("You need to login first", "error")
            return redirect(url_for('auth.login'))
        
        print(f"Looking up profile for user_id: {user_id}")
        user = User.find_by_id(ObjectId(user_id))
        profile_data = victimService.get_victim_profile(user_id)
        
        # Get cases for the victim
        cases = victimService.get_victim_cases(user_id)
        
        # Get resources
        resources = victimService.get_available_resources()
        
        # Get messages
        messages = victimService.get_victim_messages(user_id)
        
        print(f"User data: {user}")
        print(f"Profile data: {profile_data}")
        
        return render_template('victim_profile.html', 
                             profile=profile_data, 
                             user=user,
                             cases=cases,
                             resources=resources,
                             messages=messages)
    except Exception as e:
        print(f"Error in profile route: {str(e)}")
        flash("Error loading profile", "error")
        return redirect(url_for('auth.login'))

@victimProfile_bp.route('/update_profile', methods=['POST'])
@role_required('victim')
def update_profile():
    try:
        user_id = session.get("user_id")
        update_data = {
            'username': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone')
        }
        
        if victimService.update_victim_profile(user_id, update_data):
            flash("Profile updated successfully", "success")
        else:
            flash("Error updating profile", "error")
            
        return redirect(url_for('victimProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victimProfile.profile'))

@victimProfile_bp.route('/change_password', methods=['POST'])
@role_required('victim')
def change_password():
    try:
        user_id = session.get("user_id")
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        user = User.find_by_id(ObjectId(user_id))
        if not User.verify_password(user, current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('victimProfile.profile'))
        
        if User.update_password(user_id, new_password):
            flash("Password updated successfully", "success")
        else:
            flash("Error updating password", "error")
            
        return redirect(url_for('victimProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victimProfile.profile'))

@victimProfile_bp.route('/update_location', methods=['POST'])
@role_required('victim')
def update_location():
    try:
        user_id = session.get("user_id")
        location_data = {
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'location_sharing': bool(request.form.get('locationToggle'))
        }
        
        if victimService.update_victim_location(user_id, location_data):
            flash("Location updated successfully", "success")
        else:
            flash("Error updating location", "error")
            
        return redirect(url_for('victimProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victimProfile.profile'))

@victimProfile_bp.route('/send_message', methods=['POST'])
@role_required('victim')
def send_message():
    try:
        user_id = session.get("user_id")
        message_content = request.form.get('message')
        
        if victimService.send_message(user_id, message_content):
            flash("Message sent successfully", "success")
        else:
            flash("Error sending message", "error")
            
        return redirect(url_for('victimProfile.profile'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victimProfile.profile'))