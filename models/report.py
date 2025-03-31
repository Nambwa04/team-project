from flask_pymongo import PyMongo

# Initialize PyMongo instance (if not already done in your user module)
mongo = PyMongo()

class ReportModel:
    def __init__(self, mongo):
        self.collection = mongo.db.report

    # Insert a new report into the database
    def add_report(self, report_data):
        return self.collection.insert_one(report_data)

    # Retrieve all reports from the database
    def get_all_reports(self):
        return list(self.collection.find())