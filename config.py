# Description: This file contains the configuration settings for the application.
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'oruochdaniel45@gmail.com'
    MONGO_URI = os.environ.get('MONGO_URI')
    FRONTEND_URL = os.environ.get('FRONTEND_URL')

    # Admin configuration
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    ADMIN_ROLE = 'admin'

    @staticmethod
    def init_app(app):
        # You can add specific initialization code here if needed
        pass