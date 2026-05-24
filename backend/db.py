from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["career_path_allocator"]

users_collection = db["users"]
predictions_collection = db["predictions"]
academic_marks_collection = db["academic_marks"]
psychometric_data_collection = db["psychometric_data"]
strength_analysis_collection = db["strength_analysis"]

# Create unique index on email
users_collection.create_index("email", unique=True)
