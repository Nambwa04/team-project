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
    def search_resources(self, search_query):
        from bson.objectid import ObjectId
        query_conditions = [
            {"name": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}},
            {"category": {"$regex": search_query, "$options": "i"}}
        ]
        
        # If search_query is a valid ObjectId, add a condition to search by _id
        if ObjectId.is_valid(search_query):
            query_conditions.append({"_id": ObjectId(search_query)})
        
        return list(self.collection.find({"$or": query_conditions}))

    def filter_by_category(self, category):
        return list(self.collection.find({"category": category}))

    def search_resources_by_query_and_category(self, search_query, category):
        query = {
            "$and": [
                {"$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}}
                ]},
                {"category": category}
            ]
        }
        
        return list(self.collection.find(query))

    # Count the total number of resources in the database
    def count_resources(self):
        return self.collection.count_documents({})

    def filter_resources(self, filters):
        """Filter resources by multiple criteria like type and category"""
        return list(self.collection.find(filters))

    def search_resources_with_filters(self, search_query, filters=None):
        """Search resources by query text and apply additional filters"""
        from bson.objectid import ObjectId
        
        if filters is None:
            filters = {}
        
        # Create text search conditions
        query_conditions = [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}}
        ]
        
        # If search_query is a valid ObjectId, add a condition to search by _id
        if ObjectId.is_valid(search_query):
            query_conditions.append({"_id": ObjectId(search_query)})
        
        # Combine text search with filters
        query = {"$and": [
            {"$or": query_conditions}
        ]}
        
        # Add each filter to the $and conditions
        for key, value in filters.items():
            query["$and"].append({key: value})
        
        return list(self.collection.find(query))