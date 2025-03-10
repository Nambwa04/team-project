from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.victim import VictimModel
from models.user import mongo
from bson import ObjectId 

# Create Blueprint
victim_bp = Blueprint('victim', __name__)
victim_model = VictimModel(mongo)

@victim_bp.route('/manage_victims', methods=['GET'])
def manage_victims():
    victims = victim_model.get_all_victims()
    for victim in victims:
        victim['_id'] = str(victim['_id'])
    return render_template('victims.html', victims=victims)

@victim_bp.route('/add_victim', methods=['POST'])
def add_victim():
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

@victim_bp.route('/edit_victim/<victim_id>', methods=['POST'])
def edit_victim(victim_id):
    updated_victim = {
        'name': request.form.get('name'),
        'gender': request.form.get('gender'),
        'location': request.form.get('location')
    }
    if not all(updated_victim.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('victim.manage_victims'))
    try:
        result = victim_model.update_victim(victim_id, updated_victim)
        if result.modified_count:
            flash('Victim updated successfully', 'success')
        else:
            flash('No changes made or victim not found', 'error')
    except Exception as e:
        flash(f'Error updating victim: {str(e)}', 'error')
    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/delete_victim/<victim_id>', methods=['POST'])
def delete_victim(victim_id):
    try:
        result = victim_model.delete_victim(victim_id)
        if result.deleted_count:
            flash('Victim deleted successfully', 'success')
        else:
            flash('Victim not found', 'error')
    except Exception as e:
        flash(f'Error deleting victim: {str(e)}', 'error')
    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/search_victim', methods=['GET'])
def search_victim():
    search_query = request.args.get('search_query', '').strip()
    gender = request.args.get('gender', '').strip()

    # If neither search query nor gender is provided, redirect to the manage page.
    if not search_query and not gender:
        return redirect(url_for('victim.manage_victims'))
    
    # If a search query is provided, use it; otherwise, get all victims.
    if search_query:
        victims = victim_model.search_victims(search_query)
    else:
        victims = victim_model.get_all_victims()

    # If a gender filter is applied, filter the results.
    if gender:
        victims = [v for v in victims if v.get('gender', '').lower() == gender.lower()]

    # Convert ObjectId to string for each victim.
    for victim in victims:
        victim['_id'] = str(victim['_id'])

    return render_template('victims.html', victims=victims)