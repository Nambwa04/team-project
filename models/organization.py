from flask_pymongo import PyMongo

# Initialize PyMongo instance
mongo = PyMongo()

class OrganizationModel:
    def __init__(self, mongo):
        self.collection = mongo.db.organizations

    def get_all_organizations(self):
        """Retrieve all organizations from the database."""
        return list(self.collection.find())

    def add_organization(self, organization_data):
        """Add a new organization to the database."""
        return self.collection.insert_one(organization_data)

    def update_organization(self, organization_id, updated_data):
        """Update an existing organization."""
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(organization_id)},
            {'$set': updated_data}
        )

    def delete_organization(self, organization_id):
        """Delete an organization from the database."""
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(organization_id)})

    def search_organizations(self, search_query):
        """Search organizations by name or category."""
        return list(self.collection.find({
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"category": {"$regex": search_query, "$options": "i"}}
            ]
        }))
