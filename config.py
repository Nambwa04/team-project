# Description: This file contains the configuration settings for the application.
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'your_password_salt'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Correct usage of environment variable
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Correct usage of environment variable
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@yourdomain.com'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/testDatabase'
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or "http://localhost:5000"

    # Admin configuration
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'NewSecurePassword123')
    ADMIN_ROLE = 'admin'

    @staticmethod
    def init_app(app):
        # You can add specific initialization code here if needed
        pass