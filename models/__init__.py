from flask_pymongo import PyMongo

mongo = PyMongo()

from .user import User

__all__ = ['mongo', 'User']
