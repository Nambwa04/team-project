from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.report import ReportModel
from models.user import mongo

report_bp = Blueprint('report', __name__)
report_model = ReportModel(mongo)

@report_bp.route('/report', methods=['GET'])
def report_form():
    return render_template('report.html')

@report_bp.route('/report', methods=['POST'])
def submit_report():
    report_data = {
        'reporter_name': request.form.get('reporter_name'),
        'reporter_contact': request.form.get('reporter_contact'),
        'case_description': request.form.get('case_description'),
        'case_location': request.form.get('case_location')
    }
    
    if not all(report_data.values()):
        flash("All fields are required!", "error")
        return redirect(url_for('report.report_form'))
    
    try:
        report_model.add_report(report_data)
        flash("Report submitted successfully!", "success")
    except Exception as e:
        flash(f"Error submitting report: {str(e)}", "error")
    
    return redirect(url_for('report.report_form'))