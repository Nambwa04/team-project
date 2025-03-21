from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from models.user import User
from services.adminService import AdminService
from models.decorators import role_required
from bson import ObjectId

adminProfile_bp = Blueprint('adminProfile', __name__)
adminService = AdminService()

@adminProfile_bp.route('/profile')
@role_required('admin')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    profile_data = adminService.get_admin_profile(user_id)
    if profile_data:
        return render_template('admin_profile.html', profile=profile_data)
    else:
        flash("Profile not found", "error")
        return redirect(url_for('auth.login'))

@adminProfile_bp.route('/profile/update', methods=['POST'])
@role_required('admin')
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))

    user_update = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'contact': request.form.get('contact')
    }

    admin_update = {
        'department': request.form.get('department'),
        'position': request.form.get('position')
    }
    
    try:
        # Update user model data
        User.collection.update_one(
            {"_id": ObjectId(user_id)}, 
            {"$set": user_update}
        )

        # Update admin-specific data
        adminService.admins.update_one(
            {"user_id": ObjectId(user_id)}, 
            {"$set": admin_update}
        )

        flash("Profile updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating profile: {str(e)}", "error")
    
    return redirect(url_for('adminProfile.profile'))