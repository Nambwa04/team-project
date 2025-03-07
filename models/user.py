from flask_bcrypt import Bcrypt
from . import mongo

bcrypt = Bcrypt()

class User:
    collection = None  # Placeholder for MongoDB collection

    @classmethod
    def init_user(cls):
        cls.collection = mongo.db.users  # Initialize collection

    @classmethod
    def register_user(cls, username, email, password, role='victim'):
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        return cls.collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_pw,
            'role': role
        })

    @classmethod
    def find_by_username(cls, username):
        return cls.collection.find_one({"username": username})

    @classmethod
    def find_by_email(cls, email):
        return cls.collection.find_one({"email": email})

    @classmethod
    def is_admin(user):
        return user.get("role") == "admin"

    @classmethod
    def update_password(cls, user_id, new_password):
        hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
        return cls.collection.update_one(
            {"_id": user_id},
            {"$set": {"password": hashed_pw}}
        )