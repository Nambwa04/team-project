from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from models.user import mongo, User, bcrypt
from bson import ObjectId
from models.decorators import role_required
from services.organizationService import OrganizationService
from models.organization import OrganizationModel

# Create Blueprint
organization_bp = Blueprint('organization', __name__)
organization_model = OrganizationModel(mongo)

organizationService = OrganizationService()

# Define routes
@organization_bp.route('/manage_organizations', methods=['GET'])
@role_required('admin')
def manage_organizations():
    organizations = organizationService.get_all_organizations()

    # Convert ObjectId to string for JSON serialization
    processed = []
    for org in organizations:
        org['_id'] = str(org['_id'])
        if org.get('user_data'):
            org.update(org['user_data'][0])
            del org['user_data']
        processed.append(org)

    return render_template('organizations.html', organizations=processed)

@organization_bp.route('/add_organization', methods=['POST'])
def add_organization():
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    category = request.form.get('category')
    location = request.form.get('location')

    # Validate required fields
    required_fields = [username, email, phone, category, location]
    if not all(required_fields):
        flash('All fields are required!', 'error')
        return redirect(url_for('organization.manage_organizations'))

    # Check for existing email or username
    if User.find_by_email(email):
        flash('Email already exists!', 'error')
        return redirect(url_for('organization.manage_organizations'))
    if User.find_by_username(username):
        flash('Username already exists!', 'error')
        return redirect(url_for('organization.manage_organizations'))

    try:
        # Create user with default password
        default_password = "org1234"  # Set a default password
        user_id = User.register_user(username, email, default_password, role='organization').inserted_id

        # Create organization profile linked to the user
        organization_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'phone': phone,
            'category': category,
            'location': location,
        }
        organization_model.add_organization(organization_data)  # Insert into organization collection

        flash('Organization added. User can login with email and default password.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('organization.manage_organizations'))

@organization_bp.route('/organization/<organization_id>', methods=['POST'])
def edit_organization(organization_id):
    updated_organization = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'category': request.form.get('category'),
        'location': request.form.get('location')
    }
    if not all(updated_organization.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('organization.manage_organizations'))
    try:
        result = organization_model.update_organization(organization_id, updated_organization)
        if result.modified_count:
            flash('Organization updated successfully', 'success')
        else:
            flash('No changes made or organization not found', 'error')
    except Exception as e:
        flash(f'Error updating organization: {str(e)}', 'error')
    return redirect(url_for('organization.manage_organizations'))


@organization_bp.route('/organization/<organization_id>/delete', methods=['POST'])
def delete_organization(organization_id):
    try:
        result = organizationService.delete_organization(organization_id)

        if result.deleted_count:
            flash("Organization deleted successfully", "success")
        else:
            flash("Organization not found", "error")
        return redirect(url_for('organization.manage_organizations'))
        
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('organization.manage_organizations'))


@organization_bp.route('/search_organization', methods=['GET'])
def search_organization():
    search_query = request.args.get('search_query', '').strip()
    category = request.args.get('category', '').strip()

    if not search_query and not category:
        return redirect(url_for('organization.manage_organizations'))

    organizations = []
    if search_query and category:
        # Search by both query and category
        organizations = organizationService.search_organizations_by_query_and_category(search_query, category)
    elif search_query:
        # Search by query only
        organizations = organizationService.search_organizations(search_query)
    elif category:
        # Filter by category only
        organizations = organizationService.filter_by_category(category)

    # Convert ObjectId to string for template rendering
    for org in organizations:
        org['_id'] = str(org['_id'])

    return render_template('organizations.html', organizations=organizations)