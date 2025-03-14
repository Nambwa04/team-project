from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, current_app
from models import mongo
from models.user import User
from services.victimService import victimService
from models.decorators import role_required
from bson import ObjectId
from datetime import datetime
from services.location_service import LocationService
from services.sos_service import SOSService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

victimProfile_bp = Blueprint('victimProfile', __name__)

# Initialize services
location_service = LocationService()
sos_service = SOSService()

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
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'success': False, 'error': 'Invalid location data'}), 400
        
        latitude = data['latitude']
        longitude = data['longitude']
        
        # Update location in database
        location_service.update_victim_location(user_id, latitude, longitude)
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating location: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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

# SOS alert endpoint
@victimProfile_bp.route('/sos', methods=['POST'])
def trigger_sos():
    """Trigger an SOS emergency alert"""
    user_id = session.get("user_id")
    if not user_id:
        logger.error("SOS attempted without login")
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    logger.info(f"SOS triggered by user {user_id}")
    
    try:
        # Get request data
        data = request.json
        description = data.get('description', "Emergency SOS activated")
        location = data.get('location')
        
        logger.info(f"SOS data: description={description}, location={location is not None}")
        
        # Get victim info
        victim = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        victim_name = victim.get('username', 'Unknown') if victim else 'Unknown victim'
        
        logger.info(f"Victim: {victim_name}")
        
        # Create an emergency case
        emergency_case = {
            "victim_id": ObjectId(user_id),
            "victim_name": victim_name,
            "status": "PENDING",
            "priority": "HIGH",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "description": description,
            "location": location,
            "responder_id": None,
        }
        
        # Insert the emergency case
        result = mongo.db.emergency_cases.insert_one(emergency_case)
        case_id = str(result.inserted_id)
        logger.info(f"Created emergency case with ID: {case_id}")
        
        # Create an instance of the responder model and use it
        from models.responders import ResponderModel
        responder_model = ResponderModel(mongo)
        
        try:
            # Get available responders using the instance method
            active_responders = responder_model.get_available_responders()
        except Exception as e:
            print(f"Error getting available responders: {str(e)}")
            # Fallback: Get responders directly from the database
            active_responders = []
            
        # If no active responders found through the model, query the database directly
        if not active_responders:
            print("No active responders from model. Querying database directly.")
            # Find available responders directly
            active_profiles = list(mongo.db.responders.find({
                "availability": "Available",
                "status": "Active"
            }))
            
            # Extract user IDs
            responder_ids = []
            for profile in active_profiles:
                if profile.get("user_id"):
                    responder_ids.append(profile["user_id"])
            
            # Get user details
            if responder_ids:
                active_responders = list(mongo.db.users.find({
                    "_id": {"$in": responder_ids},
                    "role": "responder"
                }))
        
        # If still no active responders, notify all responders
        if not active_responders:
            logger.info("No active responders found. Alerting all responders.")
            active_responders = list(mongo.db.users.find({"role": "responder"}))
            logger.info(f"Found {len(active_responders)} total responders")
        
        # Create notifications for responders
        notification_count = 0
        for responder in active_responders:
            mongo.db.notifications.insert_one({
                "user_id": responder["_id"],
                "title": "EMERGENCY SOS ALERT",
                "message": f"{victim_name} has triggered an emergency SOS alert. Immediate assistance required.",
                "type": "emergency",
                "related_id": ObjectId(case_id),
                "created_at": datetime.utcnow(),
                "read": False
            })
            notification_count += 1
        
        logger.info(f"Notified {notification_count} responders")
        
        return jsonify({
            "success": True, 
            "message": "SOS alert sent successfully",
            "case_id": case_id,
            "responders_notified": notification_count
        }), 200
        
    except Exception as e:
        logger.exception(f"Error triggering SOS: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500