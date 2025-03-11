from flask import Flask, render_template
from config import Config
from models.user import User, bcrypt
from flask_pymongo import PyMongo
from models import mongo
from services.realtime import realtime_service 
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
mail = Mail()
mongo.init_app(app)
bcrypt.init_app(app)
realtime_service.init_app(app)
mail.init_app(app)

# Initialize User collection
User.init_user()

# Create an admin user
def create_admin():
    with app.app_context():
        admin_username = app.config["ADMIN_USERNAME"]
        admin_email = app.config["ADMIN_EMAIL"]
        admin_password = app.config["ADMIN_PASSWORD"]
        admin_role = app.config["ADMIN_ROLE"]

        if not User.find_by_email(admin_email):
            User.register_user(admin_username, admin_email, admin_password, role=admin_role)
            print("Admin user account created successfully")
        else:
            print("Admin user account already exists")

create_admin()

# Import and register blueprints
from routes.auth import auth_bp
from routes.responderRoute import responder_bp
from routes.organizationRoute import organization_bp
from routes.victimRoute import victim_bp
from routes.resourceRoute import resource_bp
from routes.reportRoute import report_bp
from routes.victimProfileRoute import victimProfile_bp
from routes.adminRoute import admin_bp
from routes.settingsRoute import settings_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(responder_bp, url_prefix='/responder')
app.register_blueprint(organization_bp, url_prefix='/organization')
app.register_blueprint(victim_bp, url_prefix='/victim')
app.register_blueprint(resource_bp, url_prefix='/resource')
app.register_blueprint(report_bp, url_prefix='/report')
app.register_blueprint(victimProfile_bp, url_prefix='/victimprofile')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(settings_bp)

@app.route('/')
def landing():
    return render_template('frontpage.html')

if __name__ == '__main__':
    # Debugging: Print all registered routes
    realtime_service.socketio.run(app, debug=True)
