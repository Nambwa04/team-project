from flask import Blueprint, request, jsonify, redirect, url_for, flash
from models.resource import ResourceModel
from models.user import mongo
from bson.objectid import ObjectId

resource_bp = Blueprint('resource', __name__)
resource_model = ResourceModel(mongo)

@resource_bp.route('/manage_resources')
def manage_resources():
    resources = resource_model.get_all_resources()
    for resource in resources:
        resource['_id'] = str(resource['_id'])
    return jsonify({'success': True, 'resources': resources}), 200

@resource_bp.route('/add_resource', methods=['POST'])
def add_resource():
    resource = {
        'title': request.form.get('title'),
        'type': request.form.get('type'),
        'link': request.form.get('link')
    }

    if not all(resource.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('resource.manage_resources'))

    try:
        resource_model.add_resource(resource)
        flash('Resource added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding resource: {str(e)}', 'error')

    return redirect(url_for('resource.manage_resources'))

@resource_bp.route('/edit_resource/<resource_id>', methods=['PUT'])
def edit_resource(resource_id):
    try:
        updated_resource = request.json

        if not all(updated_resource.values()):
            return jsonify({'success': False, 'message': 'All fields are required!'}), 400

        result = resource_model.update_resource(resource_id, updated_resource)

        if result.modified_count:
            return jsonify({'success': True, 'message': 'Resource updated successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'No changes made or resource not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@resource_bp.route('/delete_resource/<resource_id>', methods=['POST'])
def delete_resource(resource_id):
    try:
        result = resource_model.delete_resource(resource_id)

        if result.deleted_count:
            return jsonify({'success': True, 'message': 'Resource deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Resource not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500