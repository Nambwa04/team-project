from flask import Blueprint, request, render_template, redirect, url_for, flash
from models.resource import ResourceModel
from models.user import mongo
from bson.objectid import ObjectId
from models.decorators import role_required

resource_bp = Blueprint('resource', __name__)
resource_model = ResourceModel(mongo)

@resource_bp.route('/manage_resources')
@role_required('admin')
def manage_resources():
    resources = resource_model.get_all_resources()
    for resource in resources:
        resource['_id'] = str(resource['_id'])
    return render_template('resources.html', resources=resources)

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

@resource_bp.route('/edit_resource/<resource_id>', methods=['POST']) #Why POST and not PUT?
def edit_resource(resource_id):
    updated_resource = {
        'title': request.form.get('title'),
        'type': request.form.get('type'),
        'link': request.form.get('link')
    }

    if not all(updated_resource.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('resource.manage_resources'))

    try:
        result = resource_model.update_resource(resource_id, updated_resource)
        if result.modified_count:
            flash('Resource updated successfully', 'success')
        else:
            flash('No changes made or resource not found', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('resource.manage_resources'))

@resource_bp.route('/delete_resource/<resource_id>', methods=['POST'])
def delete_resource(resource_id):
    try:
        result = resource_model.delete_resource(resource_id)

        if result.deleted_count:
            flash('Resource deleted successfully', 'success')
        else:
            flash('Resource not found', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('resource.manage_resources'))

@resource_bp.route('/search_resource', methods=['GET'])
def search_resource():
    search_query = request.args.get('search_query', '').strip()
    resource_type = request.args.get('type', '').strip()

    # If no search query and no filter, redirect back to manage_resources
    if not search_query and not resource_type:
        return redirect(url_for('resource.manage_resources'))

    # Determine search criteria
    if search_query and resource_type:
        resources = resource_model.search_resources(search_query, resource_type)
    elif search_query:
        resources = resource_model.search_resources(search_query)
    elif resource_type:
        # If only filter by type is provided
        resources = list(resource_model.collection.find({"type": resource_type}))
    
    # Convert ObjectId to string for template rendering
    for resource in resources:
        resource['_id'] = str(resource['_id'])
    
    return render_template('resources.html', resources=resources)