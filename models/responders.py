from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class ResponderModel:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.responders

    # Retrieve all responders from the database
    def get_all_responders(self):
        return list(self.collection.find())

    # Insert a new responder into the database
    def add_responder(self, responder_data):
        return self.collection.insert_one(responder_data)

    # Update a responder in the database
    def update_responder(self, responder_id, updated_data):
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(responder_id)},
            {'$set': updated_data}
        )

    # Delete a responder from the database
    def delete_responder(self, responder_id):
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(responder_id)})

    # Search responders by name or ID
    def search_responders(self, search_query):
        from bson.objectid import ObjectId
        query_conditions = [
            {"name": {"$regex": search_query, "$options": "i"}},  # lowercase "name"
            {"email": {"$regex": search_query, "$options": "i"}}
        ]
        
        # If search_query is a valid ObjectId, add a condition to search by _id
        if ObjectId.is_valid(search_query):
            query_conditions.append({"_id": ObjectId(search_query)})
        
        return list(self.collection.find({"$or": query_conditions}))

    # Count the total number of responders in the database
    def count_responders(self):
        return self.collection.count_documents({})

    # Add this new method
    def get_available_responders(self):
        """Get all available responders"""
        available_responders = []
        
        # Find responder profiles where availability is "Available" and status is "Active"
        active_profiles = list(self.collection.find({
            "availability": "Available",
            "status": "Active"
        }))
        
        # For each profile, get the associated user
        for profile in active_profiles:
            if profile.get("user_id"):
                user = self.mongo.db.users.find_one({"_id": profile["user_id"]})
                if user and user.get("role") == "responder":
                    # Combine user and profile data
                    responder_data = {**user, "profile": profile}
                    available_responders.append(responder_data)
        
        return available_responders
    
    # Also add a method to get a responder by ID
    def get_responder_by_id(self, responder_id):
        """Get responder details by ID"""
        from bson.objectid import ObjectId
        
        # Convert string ID to ObjectId if needed
        if isinstance(responder_id, str):
            responder_id = ObjectId(responder_id)
            
        # First get the user data
        user = self.mongo.db.users.find_one({"_id": responder_id, "role": "responder"})
        
        if not user:
            return None
            
        # Then get the responder profile
        profile = self.collection.find_one({"user_id": responder_id})
        
        # Combine the data
        if profile:
            user["profile"] = profile
            
        return user