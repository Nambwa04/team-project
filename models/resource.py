# models/resource.py
from flask_pymongo import PyMongo

mongo = PyMongo()

class ResourceModel:
    def __init__(self, mongo):
        self.collection = mongo.db.resources

    # Retrieve all resources from the database
    def get_all_resources(self):
        return list(self.collection.find())

    # Insert a new resource into the database
    def add_resource(self, resource_data):
        return self.collection.insert_one(resource_data)

    # Update a resource in the database
    def update_resource(self, resource_id, updated_data):
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(resource_id)},
            {'$set': updated_data}
        )

    # Delete a resource from the database
    def delete_resource(self, resource_id):
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(resource_id)})

    # Search resources by title or ID 
    def search_resources(self, search_query, resource_type=None):
        from bson import ObjectId
        query_conditions = []
        # Search by title (case-insensitive)
        query_conditions.append({"title": {"$regex": search_query, "$options": "i"}})
        # If search_query is a valid ObjectId, add a condition to search by _id
        if ObjectId.is_valid(search_query):
            query_conditions.append({"_id": ObjectId(search_query)})
        # Build the overall query; if resource_type is provided, add an AND filter.
        if resource_type:
            query = {"$and": [{"$or": query_conditions}, {"type": resource_type}]}
        else:
            query = {"$or": query_conditions}
        return list(self.collection.find(query))

    # Count the total number of resources in the database
    def count_resources(self):
        return self.collection.count_documents({})