from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from models.organization import OrganizationModel
from models.user import mongo
from bson import ObjectId

# Create Blueprint
organization_bp = Blueprint('organization', __name__)
organization_model = OrganizationModel(mongo)

# Define routes
@organization_bp.route('/manage_organizations', methods=['GET'])
def manage_organizations():
    organizations = organization_model.get_all_organizations()

    # Convert ObjectId to string for JSON serialization
    for org in organizations:
        org['_id'] = str(org['_id'])

    return render_template('organizations.html', organizations=organizations)

@organization_bp.route('/add_organization', methods=['POST'])
def add_organization():
    organization = {
        'name': request.form.get('name'),
        'contact': request.form.get('contact'),
        'category': request.form.get('category'),
        'location': request.form.get('location')
    }

    if not all(organization.values()):
        flash("All fields are required!", "error")  
        return redirect(url_for('organization.manage_organizations'))

    try:
        organization_model.add_organization(organization)
        flash("Organization added successfully!", "success")  
        return redirect(url_for('organization.manage_organizations'))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")  
        return redirect(url_for('organization.manage_organizations'))

@organization_bp.route('/organization/<organization_id>', methods=['POST'])
def edit_organization(organization_id):
    try:
        updated_data = {
            'name': request.form.get('name'),
            'contact': request.form.get('contact'),
            'category': request.form.get('category'),
            'location': request.form.get('location')
        }
        if not all(updated_data.values()):
            flash("All fields are required!", "error")
            return redirect(url_for('organization.manage_organizations'))

        result = organization_model.update_organization(organization_id, updated_data)

        if result.modified_count:
            flash("Organization updated successfully", "success")
        else:
            flash("No changes made or organization not found", "error")
        return redirect(url_for('organization.manage_organizations'))

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('organization.manage_organizations'))


@organization_bp.route('/organization/<organization_id>/delete', methods=['POST'])
def delete_organization(organization_id):
    try:
        result = organization_model.delete_organization(organization_id)

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
        organizations = organization_model.search_organizations_by_query_and_category(search_query, category)
    elif search_query:
        # Search by query only
        organizations = organization_model.search_organizations(search_query)
    elif category:
        # Filter by category only
        organizations = organization_model.filter_by_category(category)

    # Convert ObjectId to string for template rendering
    for org in organizations:
        org['_id'] = str(org['_id'])

    return render_template('organizations.html', organizations=organizations)