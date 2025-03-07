from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.victim import VictimModel
from models.user import mongo, User, bcrypt
from bson import ObjectId 
from services.victimService import VictimService
from models.decorators import role_required

# Create Blueprint
victim_bp = Blueprint('victim', __name__)
victim_model = VictimModel(mongo)

victimService = VictimService()

@victim_bp.route('/manage_victims', methods=['GET'])
@ role_required('admin')
def manage_victims():
    victims = victimService.get_all_victims()
    processed=[]
    for victim in victims:
        victim['_id'] = str(victim['_id'])
        if victim.get('user_data'):
            victim.update(victim['user_data'][0])
            del victim['user_data']
        processed.append(victim)
    return render_template('victims.html', victims=processed)

@victim_bp.route('/add_victim', methods=['POST'])
def add_victim():
    # Extract form data
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    location = request.form.get('location')
    case_description = request.form.get('case_description')

    # Validate required fields
    required_fields = [username, email, gender, location]
    if not all(required_fields):
        flash('All fields are required!', 'error')
        return redirect(url_for('victim.manage_victims'))

    # Check for existing email or username
    if User.find_by_email(email):
        flash('Email already exists!', 'error')
        return redirect(url_for('victim.manage_victims'))
    if User.find_by_username(username):
        flash('Username already exists!', 'error')
        return redirect(url_for('victim.manage_victims'))

    try:
        # Create user with default password
        user_id = User.register_user(username, email, role='victim').inserted_id

        # Create victim profile linked to the user
        victim_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'phone': phone,
            'gender': gender,
            'location': location,
            'case_description': case_description  # Optional field
        }
        victim_model.add_victim(victim_data)  # Insert into victims collection

        flash('Victim added. User can login with email and default password.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/edit_victim/<victim_id>', methods=['POST'])
def edit_victim(victim_id):
    updated_victim = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'gender': request.form.get('gender'),
        'location': request.form.get('location'),
        'case_description': request.form.get('case_description')
    }
    if not all(updated_victim.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('victim.manage_victims'))
    try:
        result = victimService.update_victim_profile(
            victim_id,
            updated_victim['username'],
            updated_victim['location'],
            updated_victim['gender'],
            updated_victim['case_description']
        )
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
        result = victimService.delete_victim_profile(victim_id)
        
        if result and result.deleted_count > 0:
            flash('Victim deleted successfully', 'success')
        else:
            flash('Victim not found or deletion failed', 'error')
    except Exception as e:
        flash(f'Error deleting victim: {str(e)}', 'error')

    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/search_victim', methods=['GET'])
def search_victim():
    search_query = request.args.get('search_query', '').strip()
    gender = request.args.get('gender', '').strip()

    # Redirect if no search criteria are provided
    if not search_query and not gender:
        return redirect(url_for('victim.manage_victims'))

    # Search by query and/or gender
    victims = victimService.search_victims(search_query, gender)

    return render_template('victims.html', victims=victims)