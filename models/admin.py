from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class AdminModel:
    def __init__(self, mongo):
        self.collection = mongo.db.admins

    def get_all_admins(self):
        """Retrieve all admins from database"""
        return list(self.collection.find())

    def add_admin(self, admin_data):
        """Add a new admin to database"""
        return self.collection.insert_one(admin_data)

    def update_admin(self, admin_id, updated_data):
        """Update an existing admin"""
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(admin_id)},
            {'$set': updated_data}
        )

    def delete_admin(self, admin_id):
        """Delete an admin from database"""
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(admin_id)})

    def search_admins(self, search_query):
        """Search for admins by Name or ID"""
        return list(self.collection.find({
            "$or": [
                {"Name": {"$regex": search_query, "$options": "i"}},
                {"ID": {"$regex": search_query, "$options": "i"}}
            ]
        }))