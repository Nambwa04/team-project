from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models.responders import ResponderModel
from models.user import mongo, User
from bson.objectid import ObjectId
from models.decorators import role_required
from services.responderService import responderService
from datetime import datetime

# Create Blueprint
responder_bp = Blueprint('responder', __name__)
responder_model = ResponderModel(mongo)

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