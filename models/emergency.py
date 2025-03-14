from bson.objectid import ObjectId
from datetime import datetime

class EmergencyModel:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.emergency_cases
        
        # Ensure indexes for better query performance
        self.collection.create_index([("created_at", -1)])
        self.collection.create_index([("status", 1)])
        self.collection.create_index([("victim_id", 1)])
        self.collection.create_index([("responder_id", 1)])
        
    def create_emergency_case(self, victim_id, location=None, description=None):
        """
        Create a new emergency case when SOS button is activated
        """
        emergency_case = {
            "victim_id": ObjectId(victim_id),
            "status": "PENDING",
            "priority": "HIGH",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "description": description or "Emergency SOS activated by victim",
            "location": location,
            "responder_id": None,
            "resolution": None,
            "resolved_at": None
        }
        
        result = self.collection.insert_one(emergency_case)
        return str(result.inserted_id)
    
    def get_all_emergency_cases(self):
        """Get all emergency cases sorted by newest first"""
        return list(self.collection.find().sort("created_at", -1))
    
    def get_case_by_id(self, case_id):
        """Get a specific emergency case by ID"""
        return self.collection.find_one({"_id": ObjectId(case_id)})
    
    def get_cases_by_victim(self, victim_id):
        """Get all emergency cases for a specific victim"""
        return list(self.collection.find(
            {"victim_id": ObjectId(victim_id)}
        ).sort("created_at", -1))
    
    def get_cases_by_responder(self, responder_id):
        """Get all emergency cases assigned to a specific responder"""
        return list(self.collection.find(
            {"responder_id": ObjectId(responder_id)}
        ).sort("created_at", -1))
    
    def get_recent_emergency_cases(self, limit=10):
        """Get the most recent emergency cases"""
        return list(self.collection.find().sort("created_at", -1).limit(limit))
    
    def get_active_emergency_cases(self):
        """Get all active (non-resolved) emergency cases"""
        return list(self.collection.find(
            {"status": {"$ne": "RESOLVED"}}
        ).sort("created_at", -1))
    
    def count_cases_by_status(self, status):
        """Count emergency cases by status"""
        return self.collection.count_documents({"status": status})
    
    def assign_responder(self, case_id, responder_id):
        """Assign a responder to an emergency case"""
        result = self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {
                "$set": {
                    "responder_id": ObjectId(responder_id),
                    "status": "ASSIGNED",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def resolve_case(self, case_id, resolution):
        """Mark an emergency case as resolved"""
        result = self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {
                "$set": {
                    "status": "RESOLVED",
                    "resolution": resolution,
                    "resolved_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    def update_case_location(self, case_id, location):
        """Update the location information for an emergency case"""
        result = self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {
                "$set": {
                    "location": location,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0