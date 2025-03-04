from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId

# Initialize PyMongo instance
mongo = PyMongo()

# Function to initialize the app with PyMongo
def init_app(app):
    mongo.init_app(app)

# Initialize Bcrypt instance for password hashing
bcrypt = Bcrypt()

# Class representing a User
class User:
    @staticmethod
    def register_user(username, email, password):
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        return mongo.db.users.insert_one(
            {
                "username": username,
                "email": email,
                "password": hashed_password
            }
        )
    
    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email})
    
    @staticmethod
    def find_by_id(user_id):
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    @staticmethod
    def update_user(user_id, update_data):
        return mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )