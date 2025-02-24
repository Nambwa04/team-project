# models/resource.py
from flask_pymongo import PyMongo

mongo = PyMongo()

class ResourceModel:
    def __init__(self, mongo):
        self.collection = mongo.db.resources

    def get_all_resources(self):
        return list(self.collection.find())

    def add_resource(self, resource_data):
        return self.collection.insert_one(resource_data)

    def update_resource(self, resource_id, updated_data):
        from bson import ObjectId
        return self.collection.update_one(
            {'_id': ObjectId(resource_id)},
            {'$set': updated_data}
        )

    def delete_resource(self, resource_id):
        from bson import ObjectId
        return self.collection.delete_one({'_id': ObjectId(resource_id)})