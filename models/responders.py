from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class ResponderModel:
    def __init__(self, mongo):
        self.collection = mongo.db.responders

    def get_all_responders(self):
        """Retrieve all responders from database"""
        return list(self.collection.find())

    def add_responder(self, responder_data):
        """Add a new responder to database"""
        return self.collection.insert_one(responder_data)

    def update_responder(self, responder_id, updated_data):
        """Update an existing responder"""
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(responder_id)},
            {'$set': updated_data}
        )

    def delete_responder(self, responder_id):
        """Delete a responder from database"""
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(responder_id)})

    def search_responders(self, search_query):
        """Search for responders by Name or ID"""
        return list(self.collection.find({
            "$or": [
                {"Name": {"$regex": search_query, "$options": "i"}},
                {"ID": {"$regex": search_query, "$options": "i"}}
            ]
        }))