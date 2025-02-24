from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models.responders import ResponderModel  # Assuming the model is in models/responder.py
from models.user import mongo
from bson.objectid import ObjectId

# Create Blueprint
responder_bp = Blueprint('responder', __name__)
responder_model = ResponderModel(mongo)

@responder_bp.route('/manage_responders')
def manage_responders():
    """Retrieve all responders as JSON"""
    responders = responder_model.get_all_responders()
    
    # Convert ObjectId to string for JSON serialization
    for responder in responders:
        responder['_id'] = str(responder['_id'])

    return jsonify({'success': True, 'responders': responders}), 200

@responder_bp.route('/add_responder', methods=['POST'])
def add_responder():
    """Add a new responder"""
    responder = {
        'ID': request.form.get('ID'),
        'Name': request.form.get('Name'),
        'Contact': request.form.get('Contact'),
        'Assigned_Area': request.form.get('Assigned_Area')
    }
    
    # Validate input
    if not all(responder.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('responder.manage_responders'))
    
    try:
        responder_model.add_responder(responder)
        flash('Responder has been added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding responder: {str(e)}', 'error')
    
    return redirect(url_for('responder.manage_responders'))

@responder_bp.route('/edit_responder/<responder_id>', methods=['PUT'])
def edit_responder(responder_id):
    """Update an existing responder dynamically"""
    try:
        # Parse JSON request data
        updated_responder = request.json  

        if not all(updated_responder.values()):
            return jsonify({"success": False, "message": "All fields are required!"}), 400

        # Convert responder_id to ObjectId
        responder_obj_id = ObjectId(responder_id)

        # Update the responder in MongoDB
        result = responder_model.collection.update_one(
            {"_id": responder_obj_id},
            {"$set": updated_responder}
        )

        if result.modified_count:
            return jsonify({"success": True, "message": "Responder updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "No changes made or responder not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@responder_bp.route('/delete_responder/<responder_id>', methods=['POST'])
def delete_responder(responder_id):
    """Delete a responder dynamically by ID"""
    try:
        # Convert ID to ObjectId
        responder_obj_id = ObjectId(responder_id)

        # Check if the responder exists
        existing_responder = responder_model.collection.find_one({"_id": responder_obj_id})
        if not existing_responder:
            return jsonify({"success": False, "message": "Responder not found"}), 404

        # Delete the responder
        responder_model.collection.delete_one({"_id": responder_obj_id})
        
        return jsonify({"success": True, "message": "Responder deleted successfully"}), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@responder_bp.route('/search_responder')
def search_responder():
    """Search for responders and return JSON data"""
    search_query = request.args.get('search_query', '').strip()

    if not search_query:
        return jsonify({"success": False, "message": "Search query is required"}), 400

    responders = responder_model.search_responders(search_query)

    # Convert ObjectId to string for JSON serialization
    for responder in responders:
        responder['_id'] = str(responder['_id'])

    return jsonify({"success": True, "responders": responders}), 200