from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class VictimModel:
    def __init__(self, mongo):
        self.collection = mongo.db.victims

    # Retrieve all victims from the database
    def get_all_victims(self):
        return list(self.collection.find())

    # Insert a new victim into the database
    def add_victim(self, victim_data):
        return self.collection.insert_one(victim_data)

    # Update a victim in the database
    def update_victim(self, victim_id, updated_data):
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(victim_id)},
            {'$set': updated_data}
        )

    # Delete a victim from the database
    def delete_victim(self, victim_id):
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(victim_id)})

    # Search for victims by name or ID
    def search_victims(self, search_query):
        from bson.objectid import ObjectId
        query_conditions = [
            {"name": {"$regex": search_query, "$options": "i"}}
        ]
        if ObjectId.is_valid(search_query):
            query_conditions.append({"_id": ObjectId(search_query)})
        return list(self.collection.find({"$or": query_conditions}))

    # Count the total number of victims in the database
    def count_victims(self):
        return self.collection.count_documents({})