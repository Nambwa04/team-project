from flask import Blueprint, current_app, render_template, redirect, session, url_for, request, flash, jsonify
from models.responders import ResponderModel
from models.user import mongo, User
from bson.objectid import ObjectId
from models.decorators import role_required
from models.victim import VictimModel
from services.responderService import responderService
from datetime import datetime

# Add these imports if not already present
from models.emergency import EmergencyModel
from services.notification_service import NotificationService
from bson.objectid import ObjectId
from datetime import datetime

# Create Blueprint
responder_bp = Blueprint('responder', __name__)
responder_model = ResponderModel(mongo)

# Initialize the services
emergency_model = EmergencyModel(mongo)
notification_service = NotificationService(mongo)

@responder_bp.route('/manage_responders', methods=['GET'])
@role_required('admin')
def manage_responders():
    responders = responder_model.get_all_responders()

    # Convert ObjectId to string for template rendering
    for responder in responders:
        responder['_id'] = str(responder['_id'])

    total_responders = len(responders)  # Count total responders

    return render_template('responders.html', responders=responders, total_responders=total_responders)

@responder_bp.route('/add_responder', methods=['POST'])
def add_responder():
    try:
        # Extract form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        assigned_area = request.form.get('assigned_area')
        password = request.form.get('password')
        role = 'responder'

        # Basic validation
        if not all([name, email, password]):
            flash("Name, email, and password are required", "error")
            return redirect(url_for('responder.manage_responders'))

        # Create user account first
        user_result = User.register_user(name, email, password, role)
        if not user_result:
            flash("Failed to create user account", "error")
            return redirect(url_for('responder.manage_responders'))

        user_id = user_result.inserted_id

        # Create responder profile
        responder_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "contact": phone,  
            "assigned_area": assigned_area,
            "availability": "Available",
            "cases_handled": 0,
            "rating": 0,
            "created_at": datetime.now()
        }
        
        # Insert into responders collection
        mongo.db.responders.insert_one(responder_data)

        flash("Responder added successfully!", "success")
        return redirect(url_for('responder.manage_responders'))
    except Exception as e:
        print(f"Error in add_responder: {str(e)}")
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('responder.manage_responders'))

@responder_bp.route('/edit_responder/<responder_id>', methods=['POST'])
@role_required('admin')
def edit_responder(responder_id):
    try:
        # Extract form data
        name = request.form.get('name')
        contact = request.form.get('contact')
        assigned_area = request.form.get('assigned_area')
        
        # Validate the data
        if not all([name, contact, assigned_area]):
            flash("All fields are required", "error")
            return redirect(url_for('responder.manage_responders'))
        
        # Update the responder
        update_data = {
            'name': name,
            'contact': contact,
            'assigned_area': assigned_area
        }
        
        result = responder_model.update_responder(responder_id, update_data)
        
        if result.modified_count > 0:
            flash("Responder updated successfully", "success")
        else:
            flash("No changes were made", "info")
            
    except Exception as e:
        print(f"Error updating responder: {str(e)}")
        flash(f"Error: {str(e)}", "error")
        
    return redirect(url_for('responder.manage_responders'))

@responder_bp.route('/delete_responder/<responder_id>', methods=['POST'])
@role_required('admin')
def delete_responder(responder_id):
    try:
        responder_model.delete_responder(responder_id)
        flash('Responder deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting responder: {str(e)}', 'error')

    return redirect(url_for('responder.manage_responders'))

@responder_bp.route('/search_responder', methods=['GET'])
@role_required('admin')
def search_responder():
    search_query = request.args.get('search_query', '').strip()
    area_filter = request.args.get('area', '').strip()
    
    if not search_query and not area_filter:
        return redirect(url_for('responder.manage_responders'))
    
    # Initial search based on query – adjust as necessary to incorporate filtering directly.
    responders = responder_model.search_responders(search_query)
    
    # Apply filter for Assigned Area if provided
    if area_filter:
        responders = [r for r in responders if r.get('assigned_area') == area_filter]
    
    for responder in responders:
        responder['_id'] = str(responder['_id'])
    
    return render_template('responders.html', responders=responders)

# Add these routes for responder emergency handling
@responder_bp.route('/emergencies')
def view_emergencies():
    """View all active emergency cases"""
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    
    try:
        # Get all active emergency cases
        cases = emergency_model.get_active_emergency_cases()
        
        # Get victim details for each case
        for case in cases:
            victim = VictimModel.get_victim_by_id(case.get('victim_id'))
            if victim:
                case['victim_name'] = victim.get('name', 'Unknown')
        
        return render_template("responder/emergencies.html", cases=cases)
        
    except Exception as e:
        flash(f"Error retrieving emergency cases: {str(e)}", "error")
        return redirect(url_for('responder.dashboard'))

@responder_bp.route('/emergency/<case_id>')
def emergency_details(case_id):
    """View details of a specific emergency case"""
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    
    try:
        case = emergency_model.get_case_by_id(case_id)
        if not case:
            flash("Emergency case not found", "error")
            return redirect(url_for('responder.view_emergencies'))
        
        # Get victim details
        victim = VictimModel.get_victim_by_id(case.get('victim_id'))
        
        return render_template("responder/emergency_details.html", 
                               case=case, 
                               victim=victim)
    
    except Exception as e:
        flash(f"Error retrieving case details: {str(e)}", "error")
        return redirect(url_for('responder.view_emergencies'))

@responder_bp.route('/emergency/accept/<case_id>', methods=['POST'])
def accept_emergency(case_id):
    """Accept an emergency case assignment"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        # Assign this responder to the case
        result = emergency_model.assign_responder(case_id, user_id)
        
        if result:
            # Notify the victim
            case = emergency_model.get_case_by_id(case_id)
            responder = responder_model.get_responder_by_id(user_id)
            
            if case and responder:
                notification_service.create_notification(
                    case['victim_id'],
                    "Responder Assigned",
                    f"A responder ({responder.get('name', 'Unknown')}) has been assigned to your emergency case.",
                    "info",
                    {"case_id": case_id}
                )
            
            return jsonify({
                "success": True,
                "message": "Emergency case accepted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to accept emergency case"
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Error accepting emergency: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@responder_bp.route('/emergency/resolve/<case_id>', methods=['POST'])
def resolve_emergency(case_id):
    """Resolve an emergency case"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        resolution = request.json.get('resolution', "Case resolved by responder")
        
        # Check if this responder is assigned to the case
        case = emergency_model.get_case_by_id(case_id)
        if not case or str(case.get('responder_id')) != user_id:
            return jsonify({
                "success": False,
                "error": "You are not assigned to this emergency case"
            }), 403
        
        # Resolve the case
        result = emergency_model.resolve_case(case_id, resolution)
        
        if result:
            # Notify the victim
            notification_service.create_notification(
                case['victim_id'],
                "Emergency Case Resolved",
                f"Your emergency case has been resolved.",
                "success",
                {"case_id": case_id}
            )
            
            return jsonify({
                "success": True,
                "message": "Emergency case resolved successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to resolve emergency case"
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Error resolving emergency: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500