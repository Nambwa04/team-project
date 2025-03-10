from flask_pymongo import PyMongo
from bson.objectid import ObjectId

mongo = PyMongo()

class UserModel:
    def __init__(self, mongo):
        self.collection = mongo.db.users

    # Retrieve user in the database by ObjectId
    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
