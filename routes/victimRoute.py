from flask import Blueprint, request, jsonify, redirect, url_for, flash
from models.victim import VictimModel
from models.user import mongo
from bson import ObjectId 

# Create Blueprint
victim_bp = Blueprint('victim', __name__)
victim_model = VictimModel(mongo)

@victim_bp.route('/manage_victims', methods=['GET'])
def manage_victims():
    """Retrieve all victims as JSON"""
    victims = victim_model.get_all_victims()
    for victim in victims:
        victim['_id'] = str(victim['_id'])

    return jsonify({'success': True, 'victims': victims}), 200

@victim_bp.route('/add_victim', methods=['POST'])
def add_victim():
    """Add a new victim"""
    victim = {
        'name': request.form.get('name'),
        'gender': request.form.get('gender'),
        'location': request.form.get('location')
    }

    if not all(victim.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('victim.manage_victims'))

    try:
        victim_model.add_victim(victim)
        flash('Victim has been added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding victim: {str(e)}', 'error')

    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/edit_victim/<victim_id>', methods=['PUT'])
def edit_victim(victim_id):
    """Update an existing victim dynamically"""
    try:
        updated_victim = request.json

        if not all(updated_victim.values()):
            return jsonify({'success': False, 'message': 'All fields are required!'}), 400

        result = victim_model.update_victim(victim_id, updated_victim)

        if result.modified_count:
            return jsonify({'success': True, 'message': 'Victim updated successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'No changes made or victim not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@victim_bp.route('/delete_victim/<victim_id>', methods=['DELETE'])
def delete_victim(victim_id):
    """Delete a victim dynamically by ID"""
    try:
        result = victim_model.delete_victim(victim_id)

        if result.deleted_count:
            return jsonify({'success': True, 'message': 'Victim deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Victim not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@victim_bp.route('/search_victim', methods=['GET'])
def search_victim():
    """Search for victims and return JSON data"""
    search_query = request.args.get('search_query', '').strip()

    if not search_query:
        return jsonify({'success': False, 'message': 'Search query is required'}), 400

    victims = victim_model.search_victims(search_query)

    for victim in victims:
        victim['_id'] = str(victim['_id'])

    return jsonify({'success': True, 'victims': victims}), 200