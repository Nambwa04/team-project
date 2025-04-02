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
    organizations = organization_model.get_all_organizations()

    # Convert ObjectId to string for template rendering
    for organization in organizations:
        organization['_id'] = str(organization['_id'])

    return render_template('organizations.html', organizations=organizations)

@organization_bp.route('/add_organization', methods=['POST'])
def add_organization():
    try:
        # Extract form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        location = request.form.get('location')
        services = request.form.get('services')
        password = request.form.get('password')
        role = 'organization'  # Explicitly set role

        # Basic validation
        if not all([name, email, password]):
            flash("Name, email, and password are required", "error")
            return redirect(url_for('organization.manage_organizations'))

        # Create user account first
        user_result = User.register_user(name, email, password, role)

        if not user_result:
            flash("Failed to create user account", "error")
            return redirect(url_for('organization.manage_organizations'))

        user_id = user_result.inserted_id

        # Create organization profile
        organization_data = {
            "user_id": user_id,
            "username": name,         # Changed from name to username
            "email": email,
            "contact": phone,         # Changed from phone to contact
            "location": location,
            "services": services,
            "category": request.form.get('category', '')  # Added category field
        }
        
        # Insert into organizations collection
        organizationService.organizations.insert_one(organization_data)

        flash("Organization added successfully!", "success")
        return redirect(url_for('organization.manage_organizations'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('organization.manage_organizations'))

@organization_bp.route('/edit_organization/<organization_id>', methods=['POST'])
@role_required('admin')
def edit_organization(organization_id):
    try:
        # Extract form data
        username = request.form.get('username')
        email = request.form.get('email')
        contact = request.form.get('contact')
        category = request.form.get('category')
        location = request.form.get('location')
        
        # Validate the data
        if not all([username, email, contact, category, location]):
            flash("All fields are required", "error")
            return redirect(url_for('organization.manage_organizations'))
        
        # Update the organization
        update_data = {
            'username': username,
            'email': email,
            'contact': contact,
            'category': category,
            'location': location
        }
        
        result = organization_model.update_organization(organization_id, update_data)
        
        if result.modified_count > 0:
            flash("Organization updated successfully", "success")
        else:
            flash("No changes were made", "info")
            
    except Exception as e:
        print(f"Error updating organization: {str(e)}")
        flash(f"Error: {str(e)}", "error")
        
    return redirect(url_for('organization.manage_organizations'))

@organization_bp.route('/delete_organization/<organization_id>', methods=['POST'])
@role_required('admin')
def delete_organization(organization_id):
    try:
        organization_model.delete_organization(organization_id)
        flash('Organization deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting organization: {str(e)}', 'error')

    return redirect(url_for('organization.manage_organizations'))

@organization_bp.route('/search_organization', methods=['GET'])
@role_required('admin')
def search_organization():
    search_query = request.args.get('search_query', '')
    area = request.args.get('area', '')
    
    if area and search_query:
        # Both search and area filter
        organizations = organization_model.search_organizations_by_query_and_category(
            search_query=search_query, 
            category='', 
            location=area
        )
    elif search_query:
        # Only search
        organizations = organization_model.search_organizations(search_query)
    elif area:
        # Only area filter
        organizations = organization_model.filter_by_location(area)
    else:
        # No filters, get all
        organizations = organization_model.get_all_organizations()
    
    # Convert ObjectId to string for template rendering
    for organization in organizations:
        organization['_id'] = str(organization['_id'])
    
    total_organizations = len(organizations)
    
    return render_template('organizations.html', organizations=organizations, total_organizations=total_organizations)

@organization_bp.route('/view_organizations', methods=['GET'])
@role_required('responder')
def view_organizations():
    try:
        # Fetch all organizations
        organizations = organization_model.get_all_organizations()

        # Convert ObjectId to string for template rendering
        for organization in organizations:
            organization['_id'] = str(organization['_id'])

        # Render a template specifically for responders to view organizations
        return render_template('view_organizations.html', organizations=organizations)
    except Exception as e:
        flash(f"Error fetching organizations: {str(e)}", "error")
        return redirect(url_for('responderProfile.profile'))