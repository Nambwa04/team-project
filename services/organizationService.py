from models import mongo, User
from bson import ObjectId
from flask_mail import Message, Mail

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
        self.organization = mongo.db.organizations

    def get_all_organizations(self):
        organizations = list(self.organization.find())
        for organization in organizations:
            organization['_id'] = str(organization['_id'])
        return organizations

    def get_organization_profile(self, user_id):
        # Ensure user_id is treated as ObjectId
        try:
            if ObjectId.is_valid(user_id):
                user_id = ObjectId(user_id)
            profile = self.organization.find_one({"user_id": user_id})
            if profile:
                profile['_id'] = str(profile['_id'])
            return profile or {}
        except Exception as e:
            print(f"Error fetching organization profile: {e}")
            return {}

    def create_victim_profile(self, user_id, username, email, contact, category, location):
        if User.find_by_email(email):
            raise ValueError("Email already exists!")

        if not contact.isdigit() or len(contact) != 10:
            raise ValueError("Invalid phone number!")

        default_password = generate_default_password()

        User.register_user(username, email, default_password, role="organization")
        
        # Insert a new organization profile
        return self.organization.insert_one({
            "user_id": user_id,
            "username": username,
            "email": email,
            "contact": contact,
            "category": category,
            "location": location
        })

    def update_organization_profile(self, organization_id, username, category, location):
        organization = self.organization.find_one({"_id": ObjectId(organization_id)})
        if not organization:
            raise ValueError("Organization not found!")

        User.collection.update_one(
            {"_id": organization["user_id"]}, 
            {"$set": {"username": username}}
        )
        updated_data = {
            "username": username,
            "category": category,
            "location": location
        }

        # Update the organization profile
        return self.organization.update_one(
            {"_id": ObjectId(organization_id)}, 
            {"$set": updated_data}
        )

    def delete_organization_profile(self, organization_id):
        # Fetch the organization to get the user_id
        organization = self.organization.find_one({"_id": ObjectId(organization_id)})
        if not organization:
            raise ValueError("Organization not found")

        # Delete the corresponding user
        User.collection.delete_one({"_id": organization["user_id"]})  # Use the user_id from the victim document

        # Delete the organization profile
        return self.organization.delete_one({"_id": ObjectId(organization_id)})

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

# Instantiate OrganizationService
organizationService = OrganizationService()