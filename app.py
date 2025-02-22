from flask import Flask, render_template
from config import Config
from models.user import mongo, bcrypt
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from services.realtime import realtime_service #import the realtime_service
# from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object(Config)

#initialize mongo and bcrypt
mongo.init_app(app)
bcrypt.init_app(app)
realtime_service.init_app(app) #initialize the realtime_service

#register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def landing():
    return render_template('frontpage.html')


if __name__ == '__main__':
    realtime_service.socketio.run(app, debug=True)


