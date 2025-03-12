from models import mongo, User
from bson import ObjectId
from flask_mail import Message, Mail
from datetime import datetime

mail = Mail()

def generate_default_password():
    import random
    import string
    length = 8
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def send_password_email(email, password):
    msg = Message(
        subject="Your Account Password",
        sender="current_app.config['MAIL_USERNAME']",
        recipients=[email],
    )
    msg.body = f"Your account has been created. Your temporary password is: {password}"
    mail.send(msg)

class VictimService:
    def __init__(self):
        self.victims = mongo.db.victims

    def get_all_victims(self):
        victims = list(self.victims.find())
        for victim in victims:
            victim['_id'] = str(victim['_id'])
        return victims

    def get_victim_profile(self, user_id):
        """Get or create victim profile"""
        try:
            # First try to find existing profile
            profile = self.victims.find_one({"user_id": ObjectId(user_id)})
            
            if not profile:
                # Get user data
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    # Create default profile
                    profile = {
                        "user_id": ObjectId(user_id),
                        "username": user.get("username", ""),
                        "email": user.get("email", ""),
                        "phone": "",
                        "gender": "",
                        "location": "",
                        "case_description": "",
                        "created_at": datetime.now()
                    }
                    self.victims.insert_one(profile)
                    print(f"Created new victim profile for user: {user_id}")
            
            return profile
        except Exception as e:
            print(f"Error getting victim profile: {str(e)}")
            return None

    def create_victim_profile(self, user_id, username, email, phone, location="Unknown", gender="Unknown", case_description=""):
        if User.find_by_email(email):
            raise ValueError("Email already exists!")

        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Invalid phone number!")

        default_password = generate_default_password()

        User.register_user(username, email, default_password, role="victim")
        
        # Insert a new victim profile
        return self.victims.insert_one({
            "user_id": user_id,
            "username": username,
            "email": email,
            "phone": phone,
            "location": location,
            "gender": gender,
            "case_description": case_description
        })

    def update_victim_profile(self, user_id, update_data):
        """Update victim profile"""
        try:
            result = self.victims.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating victim profile: {str(e)}")
            return False

    def delete_victim_profile(self, victim_id):
        # Fetch the victim to get the user_id
        victim = self.victims.find_one({"_id": ObjectId(victim_id)})
        if not victim:
            raise ValueError("Victim not found")

        # Delete the corresponding user
        User.collection.delete_one({"_id": victim["user_id"]})  # Use the user_id from the victim document

        # Delete the victim profile
        return self.victims.delete_one({"_id": ObjectId(victim_id)})

    def search_victims(self, search_query=None, gender=None):
        # Build the dynamic query
        query = {"$or": []}

        # Try searching by ObjectId if the search query is a valid ID
        if search_query:
            try:
                if ObjectId.is_valid(search_query):
                    query["$or"].append({"_id": ObjectId(search_query)})
            except Exception as e:
                print(f"ObjectId error: {e}")

            # Search by username or email (case-insensitive)
            query["$or"].extend([
                {"username": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}}
            ])

        # Filter by gender if provided (case-insensitive)
        if gender:
            query["gender"] = {"$regex": f"^{gender}$", "$options": "i"}

        # If no search criteria are provided, get all victims
        if not query["$or"]:
            query.pop("$or")

        # Execute the query and convert ObjectId to string
        victims = list(self.victims.find(query))
        for victim in victims:
            victim['_id'] = str(victim['_id'])

        return victims

# Instantiate VictimService
victimService = VictimService()