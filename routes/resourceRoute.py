from flask import Blueprint, request, redirect, url_for, flash, render_template
from models.user import mongo
from bson import ObjectId
from models.decorators import role_required
from models.resource import ResourceModel

# Create Blueprint
resource_bp = Blueprint('resource', __name__)
resource_model = ResourceModel(mongo)

# Define routes
@resource_bp.route('/manage_resources', methods=['GET'])
@role_required('admin')
def manage_resources():
    resources = resource_model.get_all_resources()

    # Convert ObjectId to string for template rendering
    for resource in resources:
        resource['_id'] = str(resource['_id'])

    total_resources = len(resources)  

    return render_template('resources.html', resources=resources, total_resources=total_resources)  # Pass total_resources

@resource_bp.route('/add_resource', methods=['POST'])
@role_required('admin')
def add_resource():
    resource = {
        'title': request.form.get('title'),
        'type': request.form.get('type'),
        'link': request.form.get('link')
    }

    # Validate input
    if not all(resource.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('resource.manage_resources'))

    try:
        resource_model.add_resource(resource)
        flash('Resource has been added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding resource: {str(e)}', 'error')

    return redirect(url_for('resource.manage_resources'))

@resource_bp.route('/edit_resource/<resource_id>', methods=['POST'])
@role_required('admin')
def edit_resource(resource_id):
    try:
        # Extract form data
        title = request.form.get('title')
        type = request.form.get('type')
        link = request.form.get('link')
        
        # Validate the data
        if not all([title, type, link]):
            flash("All fields are required", "error")
            return redirect(url_for('resource.manage_resources'))
        
        # Update the resource
        update_data = {
            'title': title,
            'type': type,
            'link': link
        }
        
        result = resource_model.update_resource(resource_id, update_data)
        
        if result.modified_count > 0:
            flash("Resource updated successfully", "success")
        else:
            flash("No changes were made", "info")
            
    except Exception as e:
        print(f"Error updating resource: {str(e)}")
        flash(f"Error: {str(e)}", "error")
        
    return redirect(url_for('resource.manage_resources'))

@resource_bp.route('/delete_resource/<resource_id>', methods=['POST'])
@role_required('admin')
def delete_resource(resource_id):
    try:
        resource_model.delete_resource(resource_id)
        flash('Resource deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting resource: {str(e)}', 'error')

    return redirect(url_for('resource.manage_resources'))

@resource_bp.route('/search_resource', methods=['GET'])
@role_required('admin')
def search_resource():
    search_query = request.args.get('search_query', '')
    category = request.args.get('category', '')
    resource_type = request.args.get('type', '')  # Added type filter
    
    # Build query based on available filters
    filter_conditions = {}
    
    # Add category filter if provided
    if category:
        filter_conditions['category'] = category
    
    # Add type filter if provided
    if resource_type:
        filter_conditions['type'] = resource_type
    
    # Handle search with or without filters
    if search_query:
        resources = resource_model.search_resources_with_filters(search_query, filter_conditions)
    elif filter_conditions:
        resources = resource_model.filter_resources(filter_conditions)
    else:
        resources = resource_model.get_all_resources()
    
    # Convert ObjectId to string for template rendering
    for resource in resources:
        resource['_id'] = str(resource['_id'])
    
    total_resources = len(resources)
    
    return render_template('resources.html', resources=resources, total_resources=total_resources)