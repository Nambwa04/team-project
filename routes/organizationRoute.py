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
@role_required('admin')
def add_organization():
    organization = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'contact': request.form.get('contact'),
        'category': request.form.get('category'),
        'location': request.form.get('location')
    }

    # Validate input
    if not all(organization.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('organization.manage_organizations'))

    try:
        organization_model.add_organization(organization)
        flash('Organization has been added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding organization: {str(e)}', 'error')

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