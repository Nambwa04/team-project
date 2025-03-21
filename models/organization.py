from flask_pymongo import PyMongo
from bson import is_valid

# Initialize PyMongo instance
mongo = PyMongo()

class OrganizationModel:
    def __init__(self, mongo):
        self.collection = mongo.db.organizations

    # Retrieve all organizations from the database
    def get_all_organizations(self):
        return list(self.collection.find())

    # Insert a new organization into the database
    def add_organization(self, organization_data):
        return self.collection.insert_one(organization_data)

    # Update an organization in the database
    def update_organization(self, organization_id, updated_data):
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(organization_id)},
            {'$set': updated_data}
        )

    # Delete an organization from the database
    def delete_organization(self, organization_id):
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(organization_id)})

    # Search organizations by name or category
    def search_organizations(self, search_query):
        from bson.objectid import ObjectId
        query_conditions = [
            {"username": {"$regex": search_query, "$options": "i"}},
            {"category": {"$regex": search_query, "$options": "i"}},
            {"email": {"$regex": search_query, "$options": "i"}},
            {"contact": {"$regex": search_query, "$options": "i"}},
            {"location": {"$regex": search_query, "$options": "i"}}
        ]
        
        # If search_query is a valid ObjectId, add a condition to search by _id
        if ObjectId.is_valid(search_query):
            query_conditions.append({"_id": ObjectId(search_query)})
        
        return list(self.collection.find({"$or": query_conditions}))

    # Filter organizations by category
    def filter_by_category(self, category):
        return list(self.collection.find({"category": category}))
    
    def filter_by_location(self, location):
        return list(self.collection.find({"location": location}))

    # Search organizations by name or category and filter by category
    def search_organizations_by_query_and_category(self, search_query, category, location=None):
        query = {
            "$and": [
                {"$or": [
                    {"name": {"$regex": search_query, "$options": "i"}}
                ]},
                {"category": category}
            ]
        }
        
        if location:
            query["$and"].append({"location": location})
        
        return list(self.collection.find(query))

    # Count the total number of organizations in the database
    def count_organizations(self):
        return self.collection.count_documents({})