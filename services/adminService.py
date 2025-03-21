from models import mongo, User
from bson import ObjectId
from flask_mail import Message, Mail
from flask import current_app
from datetime import datetime

mail = Mail()

def generate_default_password():
    import secrets
    import string
    length = 12
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_password_email(email, password):
    msg = Message(
        subject="Your Admin Account Password",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email],
    )
    msg.body = f"Your admin account has been created. Your temporary password is: {password}\n\nPlease change this password after your first login for security reasons."
    mail.send(msg)

class AdminService:
    def __init__(self):
        self.admins = mongo.db.admins

    def get_all_admins(self):
        admins = list(self.admins.find())
        for admin in admins:
            admin['_id'] = str(admin['_id'])
        return admins

    def get_admin_profile(self, user_id):
        # Ensure user_id is treated as ObjectId
        try:
            if ObjectId.is_valid(user_id):
                user_id = ObjectId(user_id)
            profile = self.admins.find_one({"user_id": user_id})
            if profile:
                profile['_id'] = str(profile['_id'])
            return profile or {}
        except Exception as e:
            print(f"Error fetching admin profile: {e}")
            return {}

    def create_admin_profile(self, user_id, username, email, contact, department, position):
        if User.find_by_email(email):
            raise ValueError("Email already exists!")

        if not contact.isdigit() or len(contact) != 10:
            raise ValueError("Invalid phone number!")

        default_password = generate_default_password()

        # Create user with admin role
        User.register_user(username, email, default_password, role="admin")
        
        # Insert a new admin profile
        result = self.admins.insert_one({
            "user_id": user_id,
            "username": username,
            "email": email,
            "contact": contact,
            "department": department,
            "position": position,
            "created_at": datetime.now()
        })
        
        # Send credentials via email
        send_password_email(email, default_password)
        
        return result

    def update_admin_profile(self, admin_id, username, department, position):
        admin = self.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            raise ValueError("Admin not found!")

        User.collection.update_one(
            {"_id": admin["user_id"]}, 
            {"$set": {"username": username}}
        )
        updated_data = {
            "username": username,
            "department": department,
            "position": position,
            "updated_at": datetime.now()
        }

        # Update the admin profile
        return self.admins.update_one(
            {"_id": ObjectId(admin_id)}, 
            {"$set": updated_data}
        )

    def delete_admin_profile(self, admin_id):
        # Fetch the admin to get the user_id
        admin = self.admins.find_one({"_id": ObjectId(admin_id)})
        if not admin:
            raise ValueError("Admin not found")

        # Delete the corresponding user
        User.collection.delete_one({"_id": admin["user_id"]})

        # Delete the admin profile
        return self.admins.delete_one({"_id": ObjectId(admin_id)})

    def search_admins(self, search_query=None, department=None):
        # Build the dynamic query
        query = {"$or": []}

        # Try searching by ObjectId if the search query is a valid ID
        if search_query:
            try:
                if ObjectId.is_valid(search_query):
                    query["$or"].append({"_id": ObjectId(search_query)})
            except Exception as e:
                print(f"ObjectId error: {e}")

            # Search by username, email, or position (case-insensitive)
            query["$or"].extend([
                {"username": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}},
                {"position": {"$regex": search_query, "$options": "i"}}
            ])

        # Filter by department if provided (case-insensitive)
        if department:
            query["department"] = {"$regex": f"^{department}$", "$options": "i"}

        # If no search criteria are provided, get all admins
        if not query["$or"]:
            query.pop("$or")

        # Execute the query and convert ObjectId to string
        admins = list(self.admins.find(query))
        for admin in admins:
            admin['_id'] = str(admin['_id'])

        return admins

# Instantiate AdminService
adminService = AdminService()