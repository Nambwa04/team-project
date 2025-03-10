# Description: This file contains the configuration for the Flask app.
import os

class Config:
    SECRET_KEY = os.getenv('SECRET KEY', 'MyKey')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/testDatabase')