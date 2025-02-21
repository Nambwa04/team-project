from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

mongo = PyMongo()
bcrypt = Bcrypt()

#adds new user to the database
class User:
    @staticmethod
    def register_user(username, email, password):
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        return mongo.db.users.insert_one(
            {
                "username" : username,
                "email" : email,
                "password" : hashed_password
            }
        )
    
#finds user by email
    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one(
            {
                "email" : email
            }
        )