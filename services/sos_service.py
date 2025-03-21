from flask import current_app
from models import mongo
from bson import ObjectId
from datetime import datetime
from services.location_service import LocationService

class SOSService:
    def __init__(self):
        self.location_service = LocationService()
    
    def create_emergency_case(self, user_id, user_name, user_contact, location=None):
        """
        Create an emergency case in the database
        """
        case = {
            'victim_id': ObjectId(user_id),
            'victim_name': user_name,
            'victim_contact': user_contact,
            'type': 'EMERGENCY',
            'status': 'PENDING',
            'priority': 'HIGH',
            'created_at': datetime.utcnow(),
            'location': location,
            'responder_id': None,
            'description': 'Emergency SOS triggered by user'
        }
        
        result = mongo.db.cases.insert_one(case)
        return result.inserted_id
    
    def notify_responders(self, case_id):
        """
        Notify all available responders about an emergency case
        """
        # Get case details
        case = mongo.db.cases.find_one({'_id': case_id})
        if not case:
            return False
        
        # Find all available responders
        responders = mongo.db.users.find(
            {'role': 'responder', 'availability': 'Available'},
            {'_id': 1, 'email': 1, 'username': 1}
        )
        
        # Create notification for each responder
        for responder in responders:
            notification = {
                'user_id': responder['_id'],
                'title': 'EMERGENCY ALERT',
                'message': f'New emergency case from {case["victim_name"]}',
                'case_id': case_id,
                'created_at': datetime.utcnow(),
                'read': False,
                'type': 'emergency'
            }
            mongo.db.notifications.insert_one(notification)
        
        return True
    
    def get_active_emergency_cases(self):
        """
        Get all active emergency cases
        """
        cases = mongo.db.cases.find(
            {'type': 'EMERGENCY', 'status': {'$ne': 'CLOSED'}},
            {'_id': 1, 'victim_name': 1, 'created_at': 1, 'location': 1, 'responder_id': 1}
        ).sort('created_at', -1)
        
        return list(cases)