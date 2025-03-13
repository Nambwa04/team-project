from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.victim import VictimModel
from models.user import mongo, User, bcrypt
from bson import ObjectId 
from datetime import datetime
from services.victimService import VictimService
from models.decorators import role_required
from utils import generate_default_password 

# Create Blueprint
victim_bp = Blueprint('victim', __name__)
victim_model = VictimModel(mongo)

victimService = VictimService()

@victim_bp.route('/manage_victims', methods=['GET'])
@role_required('admin')
def manage_victims():
    try:
        # Use the VictimModel instance directly
        victims = victim_model.get_all_victims()
        
        # Process the data for display
        processed = []
        for victim in victims:
            victim_copy = dict(victim)
            if '_id' in victim_copy:
                victim_copy['_id'] = str(victim_copy['_id'])
            if 'user_id' in victim_copy:
                victim_copy['user_id'] = str(victim_copy['user_id'])
            processed.append(victim_copy)
        
        print(f"Found {len(processed)} victims")
        return render_template('victims.html', victims=processed)
    except Exception as e:
        print(f"Error in manage_victims: {str(e)}")
        flash(f"Error loading victims: {str(e)}", "error")
        return render_template('victims.html', victims=[])

@victim_bp.route('/add_victim', methods=['POST'])
def add_victim():
    try:
        # Extract form data
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        location = request.form.get('location')
        case_description = request.form.get('case_description', '')
        password = request.form.get('password', 'defaultPassword123')  # Add default password
        role = 'victim'

        # Create user account first
        user_result = User.register_user(username, email, password, role)
        
        if not user_result:
            flash("Failed to create user account", "error")
            return redirect(url_for('victim.manage_victims'))

        user_id = user_result.inserted_id
        print(f"Created user with ID: {user_id}")  # Debug log

        # Create victim profile
        victim_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "phone": phone,
            "gender": gender,
            "location": location,
            "case_description": case_description,
            "created_at": datetime.now()
        }

        # Insert into victims collection using mongo directly
        mongo.db.victims.insert_one(victim_data)
        print(f"Created victim profile for user ID: {user_id}")  # Debug log

        flash("Victim added successfully!", "success")
        return redirect(url_for('victim.manage_victims'))

    except Exception as e:
        print(f"Error in add_victim: {str(e)}")  # Debug log
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/edit_victim/<victim_id>', methods=['POST'])
def edit_victim(victim_id):
    try:
        # Collect all form data into a dictionary
        updated_data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'gender': request.form.get('gender'),
            'location': request.form.get('location'),
            'case_description': request.form.get('case_description')
        }
        
        # Validate that all required fields are provided
        if not all([updated_data['username'], updated_data['email'], updated_data['phone'], 
                   updated_data['gender'], updated_data['location']]):
            flash('All fields are required!', 'error')
            return redirect(url_for('victim.manage_victims'))
        
        # Use the update_victim method from VictimModel which supports _id directly
        result = victim_model.update_victim(victim_id, updated_data)
        
        if result.modified_count > 0:
            flash('Victim updated successfully', 'success')
        else:
            flash('No changes made or victim not found', 'error')
    except Exception as e:
        flash(f'Error updating victim: {str(e)}', 'error')
    return redirect(url_for('victim.manage_victims'))

@victim_bp.route('/delete_victim/<victim_id>', methods=['POST'])
@role_required('admin')
def delete_victim(victim_id):
    try:
        result = victim_model.delete_victim(victim_id)
        if result.deleted_count > 0:
            flash("Victim deleted successfully", "success")
        else:
            flash("Victim not found", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
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