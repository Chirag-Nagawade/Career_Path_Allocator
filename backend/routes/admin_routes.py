from flask import Blueprint, jsonify
from routes.auth_routes import token_required
from db import users_collection, predictions_collection

admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    if current_user.get('role') != 'admin':
        return jsonify({"status": False, "message": "Unauthorized access"}), 403
        
    total_users = users_collection.count_documents({})
    completed_assessments = users_collection.count_documents({"assessment_completed": True})
    users_with_photos = users_collection.count_documents({"profile_photo_path": {"$ne": None}})
    
    # Get total predictions (historical)
    total_predictions = predictions_collection.count_documents({})
    
    return jsonify({
        "status": True,
        "stats": {
            "total_users": total_users,
            "completed_assessments": completed_assessments,
            "users_with_photos": users_with_photos,
            "total_predictions": total_predictions
        }
    }), 200

@admin_routes.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    if current_user.get('role') != 'admin':
        return jsonify({"status": False, "message": "Unauthorized access"}), 403
        
    users = list(users_collection.find({}, {"password_hash": 0}).sort("created_at", -1))
    
    # Process the ObjectId to string
    for user in users:
        user['_id'] = str(user['_id'])
        
    return jsonify({
        "status": True,
        "users": users
    }), 200

@admin_routes.route('/users/<email>/details', methods=['GET'])
@token_required
def get_user_details(current_user, email):
    if current_user.get('role') != 'admin':
        return jsonify({"status": False, "message": "Unauthorized access"}), 403
        
    user = users_collection.find_one({"email": email}, {"password_hash": 0})
    if not user:
        return jsonify({"status": False, "message": "User not found"}), 404
        
    user['_id'] = str(user['_id'])
    
    # Fetch latest prediction
    pred = predictions_collection.find_one({"user_email": email}, sort=[("timestamp", -1)])
    if pred:
        pred['_id'] = str(pred['_id'])
        
    return jsonify({
        "status": True,
        "user": user,
        "latest_prediction": pred
    }), 200
