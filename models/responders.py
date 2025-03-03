from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class ResponderModel:
    def __init__(self, mongo):
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
        return list(self.collection.find({
            "$or": [
                {"Name": {"$regex": search_query, "$options": "i"}},
                {"ID": {"$regex": search_query, "$options": "i"}}
            ]
        }))

    # Count the total number of responders in the database
    def count_responders(self):
        return self.collection.count_documents({})