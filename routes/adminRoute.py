from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models.admin import AdminModel
from models.user import mongo
from bson.objectid import ObjectId

# Create Blueprint
admin_bp = Blueprint('admin', __name__)
admin_model = AdminModel(mongo)

@admin_bp.route('/manage_admins')
def manage_admins():
    """Retrieve all admins as JSON"""
    admins = admin_model.get_all_admins()
    for admin in admins:
        admin['_id'] = str(admin['_id'])
    return jsonify({'success': True, 'admins': admins}), 200

@admin_bp.route('/add_admin', methods=['POST'])
def add_admin():
    """Add a new admin"""
    admin = {
        'ID': request.form.get('ID'),
        'Name': request.form.get('Name'),
        'Contact': request.form.get('Contact'),
        'Role': request.form.get('Role')
    }
    if not all(admin.values()):
        flash('All fields are required!', 'error')
        return redirect(url_for('admin.manage_admins'))
    try:
        admin_model.add_admin(admin)
        flash('Admin has been added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding admin: {str(e)}', 'error')
    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/edit_admin/<admin_id>', methods=['PUT'])
def edit_admin(admin_id):
    """Update an existing admin dynamically"""
    try:
        updated_admin = request.json  
        if not all(updated_admin.values()):
            return jsonify({"success": False, "message": "All fields are required!"}), 400
        result = admin_model.collection.update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": updated_admin}
        )
        if result.modified_count:
            return jsonify({"success": True, "message": "Admin updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "No changes made or admin not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/delete_admin/<admin_id>', methods=['POST'])
def delete_admin(admin_id):
    """Delete an admin dynamically by ID"""
    try:
        admin_obj_id = ObjectId(admin_id)
        existing_admin = admin_model.collection.find_one({"_id": admin_obj_id})
        if not existing_admin:
            return jsonify({"success": False, "message": "Admin not found"}), 404
        admin_model.collection.delete_one({"_id": admin_obj_id})
        return jsonify({"success": True, "message": "Admin deleted successfully"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route('/search_admin')
def search_admin():
    """Search for admins and return JSON data"""
    search_query = request.args.get('search_query', '').strip()
    if not search_query:
        return jsonify({"success": False, "message": "Search query is required"}), 400
    admins = admin_model.search_admins(search_query)
    for admin in admins:
        admin['_id'] = str(admin['_id'])
    return jsonify({"success": True, "admins": admins}), 200
