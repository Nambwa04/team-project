from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from models.emergency import EmergencyModel
from models.report import ReportModel
from models.user import mongo

report_bp = Blueprint('report', __name__)

# Initialize models
report_model = ReportModel(mongo)
emergency_model = EmergencyModel(mongo)

@report_bp.route('/report', methods=['GET'])
def report_form():
    return render_template('report.html')

@report_bp.route('/submit_report', methods=['POST'])
def submit_report():
    try:
        # Step 1: Get form data
        reporter_name = request.form.get('reporter_name')
        reporter_contact = request.form.get('reporter_contact')
        case_description = request.form.get('case_description')
        case_location = request.form.get('case_location')

        # Step 2: Save the report to the 'report' collection
        report_data = {
            "reporter_name": reporter_name,
            "reporter_contact": reporter_contact,
            "case_description": case_description,
            "case_location": case_location,
            "created_at": datetime.utcnow()
        }
        report_id = report_model.collection.insert_one(report_data).inserted_id

        # Step 3: Add the case to the 'emergency_cases' collection
        emergency_case_data = {
            "description": case_description,
            "location": case_location,
            "priority": "High",  # Default priority
            "status": "PENDING",
            "report_id": report_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        emergency_case_id = emergency_model.collection.insert_one(emergency_case_data).inserted_id

        # Step 4: Trigger SOS functionality (notify responders)
        notify_responders(emergency_case_id, case_location)

        # Step 5: Provide feedback to the user
        flash("Your report has been submitted and responders have been notified.", "success")
        return redirect(url_for('report.report_form'))  # Updated endpoint name

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('report.report_form'))  # Updated endpoint name


def notify_responders(case_id, location):
    """
    Notify responders about the emergency case.
    This is a placeholder function. Replace it with your actual SOS logic.
    """
    print(f"Notifying responders about case {case_id} at location {location}")
    # Add your notification logic here (e.g., send SMS, push notifications, etc.)