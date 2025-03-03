from flask import render_template, session, redirect, url_for, flash, Blueprint
from models.victim import VictimModel
from models.responders import ResponderModel
from models.organization import OrganizationModel
from models.resource import ResourceModel
from models.user import User, mongo


admin_bp = Blueprint('admin', __name__)

victim_model = VictimModel(mongo)
responder_model = ResponderModel(mongo)
organization_model = OrganizationModel(mongo)
resource_model = ResourceModel(mongo)

@admin_bp.route('/dashboard')
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        flash("You need to login first", "error")
        return redirect(url_for('auth.login'))

    # Get real-time counts from the database
    total_victims = victim_model.count_victims()
    total_responders = responder_model.collection.count_documents({})  # or use a dedicated method
    total_organizations = organization_model.collection.count_documents({})
    total_resources = resource_model.collection.count_documents({})
    print(total_victims, total_responders, total_organizations, total_resources)
    
    return render_template("admin.html", 
                           total_victims=total_victims,
                           total_responders=total_responders,
                           total_organizations=total_organizations,
                           total_resources=total_resources)