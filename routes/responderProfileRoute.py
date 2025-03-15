from flask import Blueprint, session, render_template, redirect, url_for, flash, request, current_app
from models.emergency import EmergencyModel
from models.user import User
from services.responderService import responderService
from models.decorators import role_required
from bson import ObjectId
from datetime import datetime
from models import mongo

responderProfile_bp = Blueprint('responderProfile', __name__)

# Update the profile route to include cases

@responderProfile_bp.route('/profile')
@role_required('responder')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    
    # Get user data
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return redirect(url_for('auth.login'))
    
    print(f"Responder profile accessed by: {user.get('username', 'Unknown')}")
    
    # Get responder profile
    profile = mongo.db.responder_profiles.find_one({"user_id": ObjectId(user_id)})
    if not profile:
        profile = {}  # Initialize empty profile if not found
    
    # Count all emergency cases for debugging
    all_cases_count = mongo.db.emergency_cases.count_documents({})
    print(f"Total emergency cases in database: {all_cases_count}")
    
    # Get assigned cases
    cases = list(mongo.db.emergency_cases.find({"responder_id": ObjectId(user_id)}))
    print(f"Found {len(cases)} cases assigned to this responder")
    
    # Get ALL pending cases with high priority - no responder assigned
    # Use simpler query to match how cases are created
    emergency_cases = list(mongo.db.emergency_cases.find({
        "status": "PENDING",
        "priority": "HIGH", 
        "responder_id": None
    }).sort("created_at", -1))
    
    print(f"Found {len(emergency_cases)} emergency cases needing response")
    
    return render_template('responder_profile.html', 
                          user=user, 
                          profile=profile, 
                          cases=cases,
                          emergency_cases=emergency_cases,
                          messages=[])

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