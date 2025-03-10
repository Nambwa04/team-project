# Import necessary modules from Flask and the MongoDB model
from flask import Blueprint, session, redirect, url_for, flash, render_template
from models.user import mongo

# Create a Blueprint for the dashboard routes
dashboard_bp = Blueprint("dashboard", __name__)

# Define the route for the dashboard
@dashboard_bp.route("/dashboard")
def dashboard():
    # Check if the user is logged in by verifying the session
    if "user_id" in session:
        # Access the MongoDB collection
        collection = mongo.db.your_collection
        # Retrieve data from the collection, excluding the '_id' field
        initial_data = list(collection.find({}, {'_id': 0}))
        
        # Render the dashboard template with the username and initial data
        return render_template(
            'dashboard.html',
            username=session['username'],
            initial_data=initial_data
        )
    
    # If the user is not logged in, flash a warning message and redirect to the login page
    flash("Please login first", "warning")
    return redirect(url_for("auth.login"))