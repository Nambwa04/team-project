from flask import Blueprint, request, jsonify, redirect, url_for, flash
from models.organization import OrganizationModel
from models.user import mongo
from bson import ObjectId

# Create Blueprint
organization_bp = Blueprint('organization', __name__)
organization_model = OrganizationModel(mongo)

@organization_bp.route('/organizations', methods=['GET'])
def get_organizations():
    """Retrieve all organizations as JSON."""
    organizations = organization_model.get_all_organizations()

    # Convert ObjectId to string for JSON serialization
    for org in organizations:
        org['_id'] = str(org['_id'])

    return jsonify({'success': True, 'organizations': organizations}), 200

@organization_bp.route('/add_organization', methods=['POST'])
def add_organization():
    """Add a new organization."""
    organization = {
        'name': request.form.get('name'),
        'contact': request.form.get('contact'),
        'category': request.form.get('category'),
        'location': request.form.get('location')
    }

    if not all(organization.values()):
        return jsonify({"success": False, "message": "All fields are required!"}), 400

    try:
        organization_model.add_organization(organization)
        return jsonify({"success": True, "message": "Organization added successfully!"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@organization_bp.route('/organization/<organization_id>', methods=['PUT'])
def edit_organization(organization_id):
    """Update an existing organization."""
    try:
        updated_data = request.json
        if not all(updated_data.values()):
            return jsonify({"success": False, "message": "All fields are required!"}), 400

        result = organization_model.update_organization(organization_id, updated_data)

        if result.modified_count:
            return jsonify({"success": True, "message": "Organization updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "No changes made or organization not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@organization_bp.route('/organization/<organization_id>', methods=['DELETE'])
def delete_organization(organization_id):
    """Delete an organization."""
    try:
        result = organization_model.delete_organization(organization_id)

        if result.deleted_count:
            return jsonify({"success": True, "message": "Organization deleted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Organization not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@organization_bp.route('/search_organization', methods=['GET'])
def search_organization():
    """Search for organizations."""
    search_query = request.args.get('search_query', '').strip()

    if not search_query:
        return jsonify({"success": False, "message": "Search query is required"}), 400

    organizations = organization_model.search_organizations(search_query)

    # Convert ObjectId to string for JSON serialization
    for org in organizations:
        org['_id'] = str(org['_id'])

    return jsonify({"success": True, "organizations": organizations}), 200