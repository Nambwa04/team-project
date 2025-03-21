from models import mongo, User
from bson import ObjectId
from flask_mail import Message, Mail
from datetime import datetime

mail = Mail()

def generate_default_password():
    import random
    import string
    length = 8
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def send_password_email(email, password):
    msg = Message(
        subject="Your Account Password",
        sender="current_app.config['MAIL_USERNAME']",
        recipients=[email],
    )
    msg.body = f"Your account has been created. Your temporary password is: {password}"
    mail.send(msg)

class OrganizationService:
    def __init__(self):
        self.organizations = mongo.db.organizations
        self.messages = mongo.db.messages
        self.cases = mongo.db.cases
        self.referrals = mongo.db.referrals
        self.services = mongo.db.services

    def get_all_organizations(self):
        organizations = list(self.organizations.find())
        for organization in organizations:
            organization['_id'] = str(organization['_id'])
        return organizations

    def get_organization_profile(self, user_id):
        """Get or create organization profile"""
        try:
            profile = self.organizations.find_one({"user_id": ObjectId(user_id)})
            return profile
        except Exception as e:
            print(f"Error getting organization profile: {str(e)}")
            return None

    def create_victim_profile(self, user_id, username, email, contact, category, location):
        if User.find_by_email(email):
            raise ValueError("Email already exists!")

        if not contact.isdigit() or len(contact) != 10:
            raise ValueError("Invalid phone number!")

        default_password = generate_default_password()

        User.register_user(username, email, default_password, role="organization")
        
        # Insert a new organization profile
        return self.organizations.insert_one({
            "user_id": user_id,
            "username": username,
            "email": email,
            "contact": contact,
            "category": category,
            "location": location
        })

    def update_organization_profile(self, user_id, update_data):
        """Update organization profile"""
        try:
            result = self.organizations.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating organization profile: {str(e)}")
            return False

    def delete_organization_profile(self, organization_id):
        # Fetch the organization to get the user_id
        organization = self.organizations.find_one({"_id": ObjectId(organization_id)})
        if not organization:
            raise ValueError("Organization not found")

        # Delete the corresponding user
        User.collection.delete_one({"_id": organization["user_id"]})  # Use the user_id from the victim document

        # Delete the organization profile
        return self.organizations.delete_one({"_id": ObjectId(organization_id)})

    def search_victims(self, search_query=None, category=None):
        # Build the dynamic query
        query = {"$or": []}

        # Try searching by ObjectId if the search query is a valid ID
        if search_query:
            try:
                if ObjectId.is_valid(search_query):
                    query["$or"].append({"_id": ObjectId(search_query)})
            except Exception as e:
                print(f"ObjectId error: {e}")

            # Search by username or email (case-insensitive)
            query["$or"].extend([
                {"username": {"$regex": search_query, "$options": "i"}},
                {"email": {"$regex": search_query, "$options": "i"}}
            ])

        # Filter by category if provided (case-insensitive)
        if category:
            query["category"] = {"$regex": f"^{category}$", "$options": "i"}

        # If no search criteria are provided, get all organizations
        if not query["$or"]:
            query.pop("$or")

        # Execute the query and convert ObjectId to string
        organizations = list(self.organizations.find(query))
        for organization in organizations:
            organization['_id'] = str(organization['_id'])

        return organizations

    def send_message(self, user_id, content):
        """Send a message from the organization"""
        try:
            message = {
                "user_id": ObjectId(user_id),
                "content": content,
                "timestamp": datetime.now()
            }
            self.messages.insert_one(message)
            return True
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False

    def get_dashboard_data(self, user_id):
        """Get dashboard data for the organization"""
        try:
            active_cases = self.cases.count_documents({"organization_id": ObjectId(user_id), "status": "Active"})
            referrals = self.referrals.count_documents({"organization_id": ObjectId(user_id)})
            services_provided = self.services.count_documents({"organization_id": ObjectId(user_id)})

            dashboard_data = {
                "active_cases": active_cases,
                "referrals": referrals,
                "services_provided": services_provided
            }
            return dashboard_data
        except Exception as e:
            print(f"Error getting dashboard data: {str(e)}")
            return None

# Instantiate OrganizationService
organizationService = OrganizationService()