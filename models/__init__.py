from flask_pymongo import PyMongo
from flask_mail import Mail

mongo = PyMongo()
mail = Mail()

from .user import User

__all__ = ['mongo', 'mail', 'User']
