from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class VictimModel:
    def __init__(self, mongo):
        self.collection = mongo.db.victims

    def get_all_victims(self):
        """Retrieve all victims from the database"""
        return list(self.collection.find())

    def add_victim(self, victim_data):
        """Add a new victim to the database"""
        return self.collection.insert_one(victim_data)

    def update_victim(self, victim_id, updated_data):
        """Update an existing victim"""
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(victim_id)},
            {'$set': updated_data}
        )

    def delete_victim(self, victim_id):
        """Delete a victim from the database"""
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(victim_id)})

    def search_victims(self, search_query):
        """Search for victims by name or location"""
        return list(self.collection.find({
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"location": {"$regex": search_query, "$options": "i"}}
            ]
        }))