from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from models.user import User
from services.organizationService import OrganizationService, organizationService
from models.decorators import role_required
from bson import ObjectId
from datetime import datetime

organizationProfile_bp = Blueprint('organizationProfile', __name__)

@organizationProfile_bp.route('/profile')
@role_required('organization')
def profile():
    try:
        user_id = session.get("user_id")
        if not user_id:
            flash("You need to login first", "error")
            return redirect(url_for('auth.login'))

        # Get user data
        user = User.find_by_id(ObjectId(user_id))
        if not user:
            flash("User not found", "error")
            return redirect(url_for('auth.login'))

        # Get or create organization profile
        profile_data = organizationService.get_organization_profile(user_id)
        if not profile_data:
            # Create default profile
            profile_data = {
                "user_id": ObjectId(user_id),
                "name": user.get("username", ""),
                "email": user.get("email", ""),
                "phone": "",
                "location": "",
                "services": [],
                "created_at": datetime.now()
            }
            organizationService.organizations.insert_one(profile_data)

        print(f"User data: {user}")  # Debug log
        print(f"Profile data: {profile_data}")  # Debug log

        return render_template('organization_profile.html', organization=profile_data, user=user)
    except Exception as e:
        print(f"Error in profile route: {str(e)}")  # Debug log
        flash("Error loading profile", "error")
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