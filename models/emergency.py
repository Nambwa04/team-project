from bson.objectid import ObjectId
from datetime import datetime

from flask import current_app

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
        try:
            cases = list(self.collection.find({"responder_id": ObjectId(responder_id)}))
            # Convert ObjectIds to strings for serialization
            for case in cases:
                case["_id"] = str(case["_id"])
                # Ensure datetime objects are properly formatted
                if "created_at" in case:
                    case["created_at"] = case["created_at"]
                if "updated_at" in case:
                    case["updated_at"] = case["updated_at"]
            return cases
        except Exception as e:
            current_app.logger.error(f"Error getting cases by responder: {str(e)}")
            return []
    
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
    
    def update_case_status(self, case_id, status, notes=None):
        """Update the status of an emergency case
        
        Args:
            case_id: ID of the emergency case
            status: New status (e.g., 'PENDING', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED')
            notes: Additional notes from the responder
            
        Returns:
            Boolean indicating success
        """
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if notes:
            # Append to existing notes or create new
            case = self.get_case_by_id(case_id)
            existing_notes = case.get("notes", []) if case else []
            
            new_note = {
                "content": notes,
                "timestamp": datetime.utcnow(),
                "status": status
            }
            
            existing_notes.append(new_note)
            update_data["notes"] = existing_notes
        
        result = self.collection.update_one(
            {"_id": ObjectId(case_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    def auto_assign_responder(self, case_id, location=None):
        """
        Automatically assign the nearest available responder to an emergency case
        
        Args:
            case_id: ID of the emergency case
            location: Dictionary containing victim's location data
            
        Returns:
            Dictionary with assignment result and responder info if successful
        """
        from services.responderService import ResponderService
        
        try:
            # Get responder service instance
            responder_service = ResponderService()
            
            # Find nearest responders (max 3)
            nearest_responders = responder_service.find_nearest_responders(location, limit=3)
            
            if not nearest_responders:
                return {
                    "success": False,
                    "message": "No available responders found",
                    "responder_assigned": False
                }
            
            # Try to assign the nearest responder
            assigned = False
            assigned_responder = None
            
            for responder in nearest_responders:
                # Assign this responder to the case
                result = self.assign_responder(case_id, responder["_id"])
                
                if result:
                    assigned = True
                    assigned_responder = responder
                    break
            
            if assigned and assigned_responder:
                # Return success with responder info
                return {
                    "success": True,
                    "message": "Responder automatically assigned",
                    "responder_assigned": True,
                    "responder_id": str(assigned_responder["_id"]),
                    "responder_name": assigned_responder.get("name", "Unknown"),
                    "distance": assigned_responder.get("distance", "Unknown")
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to assign responders",
                    "responder_assigned": False
                }
                
        except Exception as e:
            print(f"Error in auto-assigning responder: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "responder_assigned": False
            }