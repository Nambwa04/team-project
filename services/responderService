from models import mongo, User
from bson import ObjectId
from flask_mail import Message, Mail
from datetime import datetime
from flask import current_app

mail = Mail()

def generate_default_password():
    import secrets
    import string
    length = 12
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_password_email(email, password):
    msg = Message(
        subject="Your Responder Account Password",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email],
    )
    msg.body = f"Your responder account has been created. Your temporary password is: {password}\n\nPlease change this password after your first login for security reasons."
    mail.send(msg)

class ResponderService:
    def __init__(self):
        self.responders = mongo.db.responders

    def get_all_responders(self):
        responders = list(self.responders.find())
        for responder in responders:
            responder['_id'] = str(responder['_id'])
        return responders

    def get_responder_profile(self, user_id):
        # Ensure user_id is treated as ObjectId
        try:
            if ObjectId.is_valid(user_id):
                user_id = ObjectId(user_id)
            profile = self.responders.find_one({"user_id": user_id})
            if profile:
                profile['_id'] = str(profile['_id'])
            return profile or {}
        except Exception as e:
            print(f"Error fetching responder profile: {e}")
            return {}

    def create_responder_profile(self, user_id, username, email, contact, specialization, location, availability="Available", experience_years=0):
        if User.find_by_email(email):
            raise ValueError("Email already exists!")

        if not contact.isdigit() or len(contact) != 10:
            raise ValueError("Invalid phone number!")

        default_password = generate_default_password()

        # Create user with responder role
        User.register_user(username, email, default_password, role="responder")
        
        # Insert a new responder profile
        result = self.responders.insert_one({
            "user_id": user_id,
            "username": username,
            "email": email,
            "contact": contact,
            "specialization": specialization,
            "location": location,
            "availability": availability,
            "experience_years": experience_years,
            "cases_handled": 0,
            "rating": 0,
            "created_at": datetime.now()
        })
        
        # Send credentials via email
        send_password_email(email, default_password)
        
        return result

    def update_responder_profile(self, responder_id, username, specialization, location, availability, experience_years):
        responder = self.responders.find_one({"_id": ObjectId(responder_id)})
        if not responder:
            raise ValueError("Responder not found!")

        User.collection.update_one(
            {"_id": responder["user_id"]}, 
            {"$set": {"username": username}}
        )
        updated_data = {
            "username": username,
            "specialization": specialization,
            "location": location,
            "availability": availability,
            "experience_years": experience_years,
            "updated_at": datetime.now()
        }

        # Update the responder profile
        return self.responders.update_one(
            {"_id": ObjectId(responder_id)}, 
            {"$set": updated_data}
        )

    def delete_responder_profile(self, responder_id):
        # Fetch the responder to get the user_id
        responder = self.responders.find_one({"_id": ObjectId(responder_id)})
        if not responder:
            raise ValueError("Responder not found")

        # Delete the corresponding user
        User.collection.delete_one({"_id": responder["user_id"]})

        # Delete the responder profile
        return self.responders.delete_one({"_id": ObjectId(responder_id)})

    def search_responders(self, search_query=None, specialization=None, location=None):
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

        # Filter by specialization if provided (case-insensitive)
        if specialization:
            query["specialization"] = {"$regex": f"^{specialization}$", "$options": "i"}
            
        # Filter by location if provided (case-insensitive)
        if location:
            query["location"] = {"$regex": location, "$options": "i"}

        # If no search criteria are provided, get all responders
        if not query["$or"] and not specialization and not location:
            query = {}
        elif not query["$or"] and (specialization or location):
            query.pop("$or")

        # Execute the query and convert ObjectId to string
        responders = list(self.responders.find(query))
        for responder in responders:
            responder['_id'] = str(responder['_id'])

        return responders

    def get_available_responders(self):
        """Get all responders with 'Available' status"""
        return list(self.responders.find({"availability": "Available"}))
    
    def update_responder_stats(self, responder_id, case_resolved=False, rating=None):
        """Update responder statistics after case completion"""
        update_data = {}
        
        if case_resolved:
            # Increment cases_handled counter
            self.responders.update_one(
                {"_id": ObjectId(responder_id)},
                {"$inc": {"cases_handled": 1}}
            )
        
        if rating:
            # Calculate new average rating
            responder = self.responders.find_one({"_id": ObjectId(responder_id)})
            current_rating = responder.get("rating", 0)
            cases_handled = responder.get("cases_handled", 0)
            
            if cases_handled > 0:
                new_rating = ((current_rating * (cases_handled - 1)) + rating) / cases_handled
                update_data["rating"] = round(new_rating, 1)
            else:
                update_data["rating"] = rating
                
            if update_data:
                self.responders.update_one(
                    {"_id": ObjectId(responder_id)},
                    {"$set": update_data}
                )

# Instantiate ResponderService
responderService = ResponderService()