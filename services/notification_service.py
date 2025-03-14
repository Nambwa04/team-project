from datetime import datetime
from bson.objectid import ObjectId

class NotificationService:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.notifications
        
        # Ensure indexes for better query performance
        self.collection.create_index([("user_id", 1)])
        self.collection.create_index([("created_at", -1)])
        self.collection.create_index([("read", 1)])
    
    def create_notification(self, user_id, title, message, type="info", data=None):
        """Create a new notification for a user"""
        notification = {
            "user_id": ObjectId(user_id),
            "title": title,
            "message": message,
            "type": type,
            "data": data or {},
            "read": False,
            "created_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(notification)
        return str(result.inserted_id)
    
    def get_user_notifications(self, user_id, limit=20):
        """Get notifications for a specific user"""
        return list(self.collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).limit(limit))
    
    def get_unread_count(self, user_id):
        """Get count of unread notifications for a user"""
        return self.collection.count_documents({
            "user_id": ObjectId(user_id),
            "read": False
        })
    
    def mark_as_read(self, notification_id):
        """Mark a notification as read"""
        result = self.collection.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"read": True}}
        )
        return result.modified_count > 0
    
    def mark_all_as_read(self, user_id):
        """Mark all notifications for a user as read"""
        result = self.collection.update_many(
            {"user_id": ObjectId(user_id), "read": False},
            {"$set": {"read": True}}
        )
        return result.modified_count