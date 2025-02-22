from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

# Initialize PyMongo instance
mongo = PyMongo()

# Function to initialize the app with PyMongo
def init_app(app):
    mongo.init_app(app)

# Initialize Bcrypt instance for password hashing
bcrypt = Bcrypt()

# Class representing a User
class User:
    # Static method to register a new user
    @staticmethod
    def register_user(username, email, password):
        # Hash the user's password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        # Insert the new user into the database
        return mongo.db.users.insert_one(
            {
                "username": username,
                "email": email,
                "password": hashed_password
            }
        )
    
    # Static method to find a user by email
    @staticmethod
    def find_by_email(email):
        # Query the database for a user with the given email
        return mongo.db.users.find_one(
            {
                "email": email
            }
        )