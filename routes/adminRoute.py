from flask import render_template, session, redirect, url_for, flash, Blueprint, jsonify, request, current_app
from models.victim import VictimModel
from models.responders import ResponderModel
from models.organization import OrganizationModel
from models.resource import ResourceModel
from models.user import User, mongo
from models.admin import AdminModel
from bson.objectid import ObjectId
from services.location_service import LocationService
from models.emergency import EmergencyModel
from datetime import datetime
from bson.json_util import dumps
import json

admin_bp = Blueprint('admin', __name__)

victim_model = VictimModel(mongo)
responder_model = ResponderModel(mongo)
organization_model = OrganizationModel(mongo)
resource_model = ResourceModel(mongo)
admin_model = AdminModel(mongo)
location_service = LocationService()
emergency_model = EmergencyModel(mongo)

@admin_bp.route('/dashboard')
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))

    # Get real-time counts from the database
    total_victims = victim_model.count_victims()
    total_responders = responder_model.collection.count_documents({})  # or use a dedicated method
    total_organizations = organization_model.collection.count_documents({})
    total_resources = resource_model.collection.count_documents({})
    print(total_victims, total_responders, total_organizations, total_resources)
    
    return render_template("admin.html", 
                           total_victims=total_victims,
                           total_responders=total_responders,
                           total_organizations=total_organizations,
                           total_resources=total_resources)

@admin_bp.route('/manage_admins')
def manage_admins():
    """Retrieve all admins as JSON"""
    admins = admin_model.get_all_admins()
    for admin in admins:
        admin['_id'] = str(admin['_id'])
    return jsonify({'success': True, 'admins': admins}), 200

@admin_bp.route('/add_admin', methods=['POST'])
def add_admin():
    """Add a new admin"""
    admin = {
        'ID': request.form.get('ID'),
        'Name': request.form.get('Name'),
        'Contact': request.form.get('Contact'),
        'Role': request.form.get('Role')
    }
    if not all(admin.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('admin.manage_admins'))
    try:
        admin_model.add_admin(admin)
        flash('Admin has been added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding admin: {str(e)}', 'error')
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/edit_admin/<admin_id>', methods=['PUT'])
def edit_admin(admin_id):
    """Update an existing admin dynamically"""
    try:
        updated_admin = request.json  
        if not all(updated_admin.values()):
            return jsonify({"success": False, "message": "All fields are required!"}), 400
        result = admin_model.collection.update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": updated_admin}
        )
        if result.modified_count:
            return jsonify({"success": True, "message": "Admin updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "No changes made or admin not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/delete_admin/<admin_id>', methods=['POST'])
def delete_admin(admin_id):
    """Delete an admin dynamically by ID"""
    try:
        admin_obj_id = ObjectId(admin_id)
        existing_admin = admin_model.collection.find_one({"_id": admin_obj_id})
        if not existing_admin:
            return jsonify({"success": False, "message": "Admin not found"}), 404
        admin_model.collection.delete_one({"_id": admin_obj_id})
        return jsonify({"success": True, "message": "Admin deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/search_admin')
def search_admin():
    """Search for admins and return JSON data"""
    search_query = request.args.get('search_query', '').strip()
    if not search_query:
        return jsonify({"success": False, "message": "Search query is required"}), 400
    admins = admin_model.search_admins(search_query)
    for admin in admins:
        admin['_id'] = str(admin['_id'])
    return jsonify({"success": True, "admins": admins}), 200

@admin_bp.route('/victim-locations')
def get_victim_locations():
    # Check if user is admin (this should already be handled by your auth middleware)
    
    try:
        # Get all victim locations
        locations = location_service.get_all_victim_locations()
        
        # Convert ObjectId to string for JSON serialization
        for location in locations:
            location['_id'] = str(location['_id'])
        
        return jsonify({
            'success': True,
            'locations': locations
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting victim locations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/emergency-cases')
def emergency_cases():
    """View all emergency cases"""
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    
    # Get all emergency cases
    cases = emergency_model.get_all_emergency_cases()
    
    # Calculate stats
    stats = {
        "pending": emergency_model.count_cases_by_status("PENDING"),
        "assigned": emergency_model.count_cases_by_status("ASSIGNED"),
        "in_progress": emergency_model.count_cases_by_status("IN_PROGRESS"),
        "resolved": emergency_model.count_cases_by_status("RESOLVED"),
    }
    
    return render_template("case.html", cases=cases, stats=stats)

@admin_bp.route('/emergency-case/<case_id>')
def emergency_case_details(case_id):
    """View details of a specific emergency case"""
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    
    try:
        case = emergency_model.get_case_by_id(case_id)
        if not case:
            flash("Emergency case not found", "error")
            return redirect(url_for('admin.emergency_cases'))
        
        # Convert note timestamps to datetime objects
        if "notes" in case:
            for note in case["notes"]:
                if isinstance(note.get("timestamp"), str):
                    try:
                        note["timestamp"] = datetime.fromisoformat(note["timestamp"])
                    except ValueError:
                        note["timestamp"] = None  # Handle invalid timestamp formats
        
        # Get victim details
        victim = victim_model.get_victim_by_id(case.get('victim_id'))
        
        # Get assigned responder details if any
        responder = None
        if case.get('responder_id'):
            responder = responder_model.get_responder_by_id(case.get('responder_id'))
        
        return render_template("case_details.html", 
                               case=case, 
                               victim=victim, 
                               responder=responder)
    
    except Exception as e:
        flash(f"Error retrieving case details: {str(e)}", "error")
        return redirect(url_for('admin.emergency_cases'))

@admin_bp.route('/api/emergency-cases')
def get_emergency_cases():
    """API endpoint to get all emergency cases as JSON"""
    try:
        cases = emergency_model.get_all_emergency_cases()
        # Convert ObjectId to string for JSON serialization
        cases_json = json.loads(dumps(cases))
        
        return jsonify({
            'success': True,
            'cases': cases_json
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error getting emergency cases: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/assign-responder', methods=['POST'])
def assign_responder():
    """Assign a responder to an emergency case"""
    try:
        data = request.json
        case_id = data.get('case_id')
        responder_id = data.get('responder_id')
        
        if not case_id or not responder_id:
            return jsonify({
                'success': False,
                'error': 'Case ID and Responder ID are required'
            }), 400
        
        result = emergency_model.assign_responder(case_id, responder_id)
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Responder assigned successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to assign responder'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error assigning responder: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/emergency-dashboard')
def emergency_dashboard_data():
    """Get data for the emergency dashboard"""
    try:
        # Get counts of different types of cases
        pending_count = emergency_model.count_cases_by_status("PENDING")
        assigned_count = emergency_model.count_cases_by_status("ASSIGNED")
        resolved_count = emergency_model.count_cases_by_status("RESOLVED")
        
        # Get recent cases 
        recent_cases = emergency_model.get_recent_emergency_cases(5)
        recent_cases_json = json.loads(dumps(recent_cases))
        
        # Get active responders
        active_responders = responder_model.get_available_responders()
        active_responders_json = json.loads(dumps(active_responders))
        
        return jsonify({
            'success': True,
            'stats': {
                'pending': pending_count,
                'assigned': assigned_count,
                'resolved': resolved_count,
                'total': pending_count + assigned_count + resolved_count
            },
            'recent_cases': recent_cases_json,
            'active_responders': active_responders_json
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/edit-case/<case_id>', methods=['GET', 'POST'])
def edit_case(case_id):
    """Edit an emergency case"""
    user_id = session.get("user_id")
    if not user_id or session.get("role") != "admin":
        flash("You need admin privileges to edit cases", "error")
        return redirect(url_for('auth.login'))
    
    try:
        case = emergency_model.get_case_by_id(case_id)
        if not case:
            flash("Emergency case not found", "error")
            return redirect(url_for('admin.emergency_cases'))
        
        if request.method == 'POST':
            # Collect form data
            description = request.form.get('description')
            priority = request.form.get('priority')
            status = request.form.get('status')
            responder_id = request.form.get('responder_id')
            
            # Prepare update data
            update_data = {
                "description": description,
                "priority": priority,
                "status": status,
                "updated_at": datetime.now()
            }
            
            # Handle responder assignment
            if responder_id:
                # Check if responder exists
                responder = responder_model.get_responder_by_id(responder_id)
                if responder:
                    update_data["responder_id"] = ObjectId(responder_id)
                    
                    # Add a note about responder assignment
                    responder_name = responder.get('name', 'Unknown responder')
                    note = {
                        "status": status,
                        "content": f"Admin assigned {responder_name} to this case",
                        "timestamp": datetime.now(),
                        "user_id": user_id
                    }
                    
                    # Update the case with the new responder and note
                    result = mongo.db.emergency_cases.update_one(
                        {"_id": ObjectId(case_id)},
                        {
                            "$set": update_data,
                            "$push": {"notes": note}
                        }
                    )
                else:
                    # If responder doesn't exist, just update the case without changing responder
                    result = mongo.db.emergency_cases.update_one(
                        {"_id": ObjectId(case_id)},
                        {"$set": update_data}
                    )
            else:
                # If no responder selected, just update the case
                result = mongo.db.emergency_cases.update_one(
                    {"_id": ObjectId(case_id)},
                    {"$set": update_data}
                )
            
            if result.modified_count > 0:
                flash("Emergency case updated successfully", "success")
            else:
                flash("No changes were made", "info")
                
            return redirect(url_for('admin.emergency_case_details', case_id=case_id))
        
        # Get all responders for dropdown
        responders = responder_model.get_all_responders()
        
        # Convert ObjectId to string for template
        case['_id'] = str(case['_id'])
        if 'responder_id' in case:
            case['responder_id'] = str(case['responder_id'])
        
        return render_template("edit_case.html", case=case, responders=responders)
        
    except Exception as e:
        flash(f"Error editing case: {str(e)}", "error")
        return redirect(url_for('admin.emergency_cases'))

@admin_bp.route('/delete-case/<case_id>', methods=['POST'])
def delete_case(case_id):
    """Delete an emergency case"""
    user_id = session.get("user_id")
    if not user_id or session.get("role") != "admin":
        flash("You need admin privileges to delete cases", "error")
        return redirect(url_for('auth.login'))
    
    try:
        # Check if the case exists
        case = emergency_model.get_case_by_id(case_id)
        if not case:
            flash("Emergency case not found", "error")
            return redirect(url_for('admin.emergency_cases'))
        
        print(f"Attempting to delete case with ID: {case_id}")
        result = mongo.db.emergency_cases.delete_one({"_id": ObjectId(case_id)})
        print(f"Deleted count: {result.deleted_count}")
        
        if result.deleted_count > 0:
            flash("Emergency case deleted successfully", "success")
        else:
            flash("Failed to delete emergency case", "error")
            
        return redirect(url_for('admin.emergency_cases'))
        
    except Exception as e:
        flash(f"Error deleting case: {str(e)}", "error")
        return redirect(url_for('admin.emergency_cases'))