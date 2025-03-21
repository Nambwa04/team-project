from flask_bcrypt import Bcrypt
from . import mongo
from bson.objectid import ObjectId
from datetime import datetime

bcrypt = Bcrypt()

class User:
    collection = None

    @classmethod
    def init_collection(cls):
        if cls.collection is None:
            cls.collection = mongo.db.users
        return cls.collection

    @classmethod
    def register_user(cls, username, email, password, role='victim'):
        cls.init_collection()  # Ensure collection is initialized
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Registering user with hash: {hashed_pw}")  # Debug log
        return cls.collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_pw,
            'role': role,
            'created_at': datetime.utcnow()
        })

    @classmethod
    def find_by_username(cls, username):
        cls.init_collection()  # Ensure collection is initialized
        return cls.collection.find_one({"username": username})

    @classmethod
    def find_by_email(cls, email):
        """Find a user by their email"""
        cls.init_collection()  # Ensure collection is initialized
        try:
            print(f"Looking up user with email: {email}")  # Debug log
            user = cls.collection.find_one({"email": email})
            print(f"Found user: {user}")  # Debug log
            return user
        except Exception as e:
            print(f"Error finding user by email: {str(e)}")  # Debug log
            return None

    @classmethod
    def find_by_id(cls, user_id):
        """Find a user by their ID"""
        cls.init_collection()
        try:
            return cls.collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            print(f"Error finding user by ID: {str(e)}")
            return None

    @classmethod
    def update_password(cls, user_id, plain_password):
        cls.init_collection()  # Ensure collection is initialized
        try:
            # Generate new password hash
            hashed_pw = bcrypt.generate_password_hash(plain_password).decode('utf-8')
            print(f"Generated hash for plain password: {hashed_pw}")
            
            # Update password in database
            result = cls.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": hashed_pw}}
            )
            
            # Verify the update
            updated_user = cls.collection.find_one({"_id": ObjectId(user_id)})
            print(f"Stored password hash: {updated_user['password']}")
            
            # Test password verification
            verification = bcrypt.check_password_hash(updated_user['password'], plain_password)
            print(f"Password verification test: {verification}")
            print(f"Plain password used: {plain_password}")
            
            return result
        except Exception as e:
            print(f"Error updating password: {str(e)}")
            raise

    @classmethod
    def verify_password(cls, user, password):
        cls.init_collection()  # Ensure collection is initialized
        try:
            print(f"Attempting to verify password for user: {user['email']}")  # Debug log
            print(f"Stored hash: {user['password']}")  # Debug log
            print(f"Attempting to verify with password: {password}")  # Debug log
            
            result = bcrypt.check_password_hash(user['password'], password)
            print(f"Password verification result: {result}")  # Debug log
            
            if not result:
                # Additional debugging information
                test_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                print(f"Test hash generated from provided password: {test_hash}")
                print(f"Length of stored hash: {len(user['password'])}")
                print(f"Length of test hash: {len(test_hash)}")
            
            return result
        except Exception as e:
            print(f"Error verifying password: {str(e)}")  # Debug log
            return False