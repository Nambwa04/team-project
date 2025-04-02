from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import mongo
from models.emergency import EmergencyModel
from models.user import User
from datetime import datetime
from bson.objectid import ObjectId

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/cases')
def view_cases():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to view emergency cases', 'error')
        return redirect(url_for('auth.login'))
    
    # Initialize the emergency model
    emergency_model = EmergencyModel(mongo)
    
    # Get filter parameters
    status = request.args.get('status', 'all')
    responder_id = request.args.get('responder_id', None)
    responder_name = None
    if responder_id:
        responder = mongo.db.responders.find_one({"_id": ObjectId(responder_id)})
        if responder:
            responder_name = responder.get("responder_name", "Unknown")
    
    # Get cases based on filters
    if status != 'all' and responder_id:
        # Filter by both status and responder
        cases = list(mongo.db.emergency_cases.find({
            "status": status,
            "responder_id": ObjectId(responder_id)
        }).sort("created_at", -1))
    elif status != 'all':
        # Filter by status only
        cases = list(mongo.db.emergency_cases.find({
            "status": status
        }).sort("created_at", -1))
    elif responder_id:
        # Filter by responder only
        cases = emergency_model.get_cases_by_responder(responder_id)
    else:
        # No filters - get all cases
        cases = emergency_model.get_all_emergency_cases()
    
    # Get all available responders for the filter dropdown
    responders = list(mongo.db.responders.find())
    
    # Get stats for the dashboard
    stats = {
        "pending": emergency_model.count_cases_by_status("PENDING"),
        "assigned": emergency_model.count_cases_by_status("ASSIGNED"),
        "in_progress": emergency_model.count_cases_by_status("IN_PROGRESS"),
        "resolved": emergency_model.count_cases_by_status("RESOLVED")
    }
    
    # Enrich case data with victim and responder information
    for case in cases:
        # Add victim info
        if case.get("victim_id"):
            victim = mongo.db.victims.find_one({"_id": ObjectId(case["victim_id"])})
            if victim:
                case["victim_name"] = victim.get("username", "Unknown")

        # Add responder info
        case["responder_name"] = case.get("responder_name", "Unassigned")  # Fetch responder_name directly
    
    return render_template('case.html', 
                          cases=cases, 
                          responders=responders,
                          stats=stats,
                          status=status,
                          responder_id=responder_id)

@emergency_bp.route('/case/<case_id>')
def case_details(case_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to view case details', 'error')
        return redirect(url_for('auth.login'))
    
    # Initialize the emergency model
    emergency_model = EmergencyModel(mongo)
    
    # Get the case
    case = emergency_model.get_case_by_id(case_id)
    
    if not case:
        flash('Case not found', 'error')
        return redirect(url_for('admin.emergency_cases'))
    
    # Get victim info
    victim = None
    if case.get("victim_name"):
        victim = {}

    # Get responder info
    responder = None
    if case.get("responder_id"):
            responder = {}
    
    return render_template('case_details.html', 
                          case=case,
                          victim=victim,
                          responder=responder)

@emergency_bp.route('/assign_case', methods=['POST'])
def assign_case():
    # Check if user is logged in and is a responder
    if 'user_id' not in session or session.get('role') != 'responder':
        flash('You do not have permission to assign cases', 'error')
        return redirect(url_for('auth.login'))
    
    case_id = request.form.get('case_id')
    responder_id = session.get('user_id')
    
    # Initialize the emergency model
    emergency_model = EmergencyModel(mongo)
    
    # Assign the case
    result = emergency_model.assign_responder(case_id, responder_id)
    
    if result:
        flash('Case assigned successfully!', 'success')
    else:
        flash('Failed to assign case', 'error')
    
    return redirect(url_for('admin.emergency_cases'))

@emergency_bp.route('/update_case_status', methods=['POST'])
def update_case_status():
    # Check if user is logged in and is a responder
    if 'user_id' not in session or session.get('role') != 'responder':
        flash('You do not have permission to update case status', 'error')
        return redirect(url_for('auth.login'))
    
    case_id = request.form.get('case_id')
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    # Initialize the emergency model
    emergency_model = EmergencyModel(mongo)
    
    # Check if the responder is assigned to this case
    case = emergency_model.get_case_by_id(case_id)
    if not case or str(case.get('responder_id')) != session.get('user_id'):
        flash('You are not assigned to this case', 'error')
        return redirect(url_for('admin.emergency_cases'))
    
    # Update the case status
    result = emergency_model.update_case_status(case_id, status, notes)
    
    if result:
        flash(f'Case status updated to {status}!', 'success')
    else:
        flash('Failed to update case status', 'error')
    
    return redirect(url_for('admin.emergency_cases'))