from flask import Flask, render_template
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

#initialize mongo and bcrypt
from models.user import mongo, bcrypt
mongo.init_app(app)
bcrypt.init_app(app)

# route importation
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.responderRoute import responder_bp
from routes.organizationRoute import organization_bp
from routes.victimRoute import victim_bp
from routes.resourceRoutes import resource_bp

from services.realtime import realtime_service #import the realtime_service
realtime_service.init_app(app) #initialize the realtime_service

#register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(responder_bp)
app.register_blueprint(organization_bp)
app.register_blueprint(victim_bp)
app.register_blueprint(resource_bp)

@app.route('/')
def landing():
    return render_template('frontpage.html')


if __name__ == '__main__':
    realtime_service.socketio.run(app, debug=True)