from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from models.user import User
from services.organizationService import OrganizationService
from models.decorators import role_required
from bson import ObjectId

organizationProfile_bp = Blueprint('organizationProfile', __name__)
organizationService = OrganizationService()

@organizationProfile_bp.route('/profile')
@role_required('organization')
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))
    profile_data = organizationService.get_organization_profile(user_id)
    if profile_data:
        return render_template('organization_profile.html', profile=profile_data)
    else:
        flash("Profile not found", "error")
        return redirect(url_for('auth.login'))

@organizationProfile_bp.route('/profile/update', methods=['POST'])
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

    organization_update = {
        'category': request.form.get('category'),
        'location': request.form.get('location')
    }
    
    # using user model for updates
    User.collection.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": user_update}
    )

    organizationService.organizations.update_one(
        {"user_id": ObjectId(user_id)}, 
        {"$set": organization_update}
    )

    if user_update or organization_update:
        flash("Profile updated successfully!", "success")
    else:
        flash("No changes made.", "info")
    return redirect(url_for('organizationProfile.profile'))