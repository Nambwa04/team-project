from flask_bcrypt import Bcrypt
from . import mongo
from bson.objectid import ObjectId

# Create a single bcrypt instance
bcrypt = Bcrypt()

class User:
    collection = None  # Placeholder for MongoDB collection

    @classmethod
    def init_user(cls):
        cls.collection = mongo.db.users  # Initialize collection

    @classmethod
    def register_user(cls, username, email, password, role='victim'):
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Registering user with hash: {hashed_pw}")  # Debug log
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
    def update_password(cls, user_id, plain_password):
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