from flask import Blueprint, render_template, redirect, url_for, request, flash
from models.responders import ResponderModel
from models.user import mongo
from bson.objectid import ObjectId

# Create Blueprint
responder_bp = Blueprint('responder', __name__)
responder_model = ResponderModel(mongo)

@responder_bp.route('/manage_responders', methods=['GET'])
def manage_responders():
    responders = responder_model.get_all_responders()

    # Convert ObjectId to string for template rendering
    for responder in responders:
        responder['_id'] = str(responder['_id'])

    return render_template('responders.html', responders=responders)

@responder_bp.route('/add_responder', methods=['POST'])
def add_responder():
    responder = {
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

@responder_bp.route('/edit_responder/<responder_id>', methods=['POST'])
def edit_responder(responder_id):
    try:
        updated_responder = {
            'Name': request.form.get('Name'),
            'Contact': request.form.get('Contact'),
            'Assigned_Area': request.form.get('Assigned_Area')
        }

        if not all(updated_responder.values()):
            flash('All fields are required!', 'error')
            return redirect(url_for('responder.manage_responders'))

        responder_model.update_responder(responder_id, updated_responder)
        flash('Responder updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating responder: {str(e)}', 'error')

    return redirect(url_for('responder.manage_responders'))

@responder_bp.route('/delete_responder/<responder_id>', methods=['POST'])
def delete_responder(responder_id):
    try:
        responder_model.delete_responder(responder_id)
        flash('Responder deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting responder: {str(e)}', 'error')

    return redirect(url_for('responder.manage_responders'))

@responder_bp.route('/search_responder', methods=['GET'])
def search_responder():
    search_query = request.args.get('search_query', '').strip()
    area_filter = request.args.get('area', '').strip()
    
    if not search_query and not area_filter:
        return redirect(url_for('responder.manage_responders'))
    
    # Initial search based on query – adjust as necessary to incorporate filtering directly.
    responders = responder_model.search_responders(search_query)
    
    # Apply filter for Assigned Area if provided
    if area_filter:
        responders = [r for r in responders if r.get('Assigned_Area') == area_filter]
    
    for responder in responders:
        responder['_id'] = str(responder['_id'])
    
    return render_template('responders.html', responders=responders)