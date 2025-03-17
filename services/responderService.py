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
        self.messages = mongo.db.messages  # Add this line

    def get_all_responders(self):
        responders = list(self.responders.find())
        for responder in responders:
            responder['_id'] = str(responder['_id'])
        return responders

    def get_responder_profile(self, user_id):
        """Get or create responder profile"""
        try:
            profile = self.responders.find_one({"user_id": ObjectId(user_id)})
            if not profile:
                # Get user data
                user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    # Create default profile
                    profile = {
                        "user_id": ObjectId(user_id),
                        "name": user.get("username", ""),
                        "email": user.get("email", ""),
                        "phone": "",
                        "assigned_area": "",
                        "availability": "Available",
                        "cases_handled": 0,
                        "rating": 0,
                        "created_at": datetime.now()
                    }
                    self.responders.insert_one(profile)
            return profile
        except Exception as e:
            print(f"Error getting responder profile: {str(e)}")
            return None

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

    def create_responder(self, name, email, phone, assigned_area, user_id):
        """Create a new responder profile"""
        try:
            # Create responder profile
            responder_data = {
                "user_id": ObjectId(user_id),  # Ensure user_id is ObjectId
                "name": name,
                "email": email,
                "contact": phone,  
                "assigned_area": assigned_area,
                "availability": "Available",
                "cases_handled": 0,
                "rating": 0,
                "created_at": datetime.now()
            }
            
            result = self.responders.insert_one(responder_data)
            print(f"Responder profile created with ID: {result.inserted_id}")
            return result

        except Exception as e:
            print(f"Error creating responder profile: {e}")
            raise

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

    def send_message(self, user_id, content):
        try:
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            message = {
                "sender_id": ObjectId(user_id),
                "sender_username": user["username"],
                "content": content,
                "timestamp": datetime.now()
            }
            self.messages.insert_one(message)
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False

    def get_responder_messages(self, user_id):
        try:
            return list(self.messages.find({
                "$or": [
                    {"sender_id": ObjectId(user_id)},
                    {"receiver_id": ObjectId(user_id)}
                ]
            }).sort("timestamp", -1))
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []

    def find_nearest_responders(self, victim_location, limit=5):
        """Find the nearest available responders to a victim location
        
        Args:
            victim_location: Dict with 'latitude' and 'longitude' keys
            limit: Maximum number of responders to return
            
        Returns:
            List of nearest responder documents sorted by proximity
        """
        if not victim_location or 'latitude' not in victim_location or 'longitude' not in victim_location:
            # If no location provided, just return available responders
            return list(self.responders.find({"availability": "Available"}).limit(limit))
            
        # Get all available responders
        available_responders = list(self.responders.find({"availability": "Available"}))
        
        # Calculate distance for each responder (if they have location data)
        responders_with_distance = []
        for responder in available_responders:
            responder_location = responder.get('last_location', {})
            if responder_location and 'latitude' in responder_location and 'longitude' in responder_location:
                # Calculate distance using Haversine formula
                distance = self._calculate_distance(
                    victim_location['latitude'], 
                    victim_location['longitude'],
                    responder_location['latitude'], 
                    responder_location['longitude']
                )
                responder['distance'] = distance
                responders_with_distance.append(responder)
            else:
                # Responders without location go at the end with "unknown" distance
                responder['distance'] = float('inf')
                responders_with_distance.append(responder)
        
        # Sort responders by distance (nearest first)
        responders_with_distance.sort(key=lambda r: r['distance'])
        
        # Return limited number of nearest responders
        return responders_with_distance[:limit]
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        from math import radians, sin, cos, sqrt, atan2
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        radius = 6371  # Radius of Earth in kilometers
        distance = radius * c
        
        return distance

# Instantiate ResponderService
responderService = ResponderService()