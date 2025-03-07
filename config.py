# Description: This file contains the configuration settings for the application.
import os

class Config:
    SECRET_KEY = os.getenv('SECRET KEY', 'MyKey')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/testDatabase')
    FRONTEND_URL = "http://localhost:5000"
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''

    #Admin configuration
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'NewSecurePassword123')
    ADMIN_ROLE = 'admin'