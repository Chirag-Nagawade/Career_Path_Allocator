from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from routes.auth_routes import token_required
from db import users_collection

profile_routes = Blueprint('profile_routes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_routes.route('', methods=['GET'])
@token_required
def get_profile(current_user):
    user_data = {
        "full_name": current_user.get("full_name"),
        "email": current_user.get("email"),
        "role": current_user.get("role"),
        "assessment_completed": current_user.get("assessment_completed"),
        "profile_photo_path": current_user.get("profile_photo_path"),
        "created_at": current_user.get("created_at")
    }
    return jsonify({"status": True, "profile": user_data}), 200

@profile_routes.route('', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"status": False, "message": "No data provided"}), 400

    update_fields = {}
    if "full_name" in data:
        update_fields["full_name"] = data["full_name"]
        
    if not update_fields:
        return jsonify({"status": False, "message": "No valid fields to update"}), 400

    users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": update_fields}
    )

    return jsonify({"status": True, "message": "Profile updated successfully"}), 200

@profile_routes.route('/photo', methods=['POST'])
@token_required
def upload_photo(current_user):
    if 'photo' not in request.files:
        return jsonify({"status": False, "message": "No file part"}), 400
        
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"status": False, "message": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user['email']}_{file.filename}")
        
        # Save path relative to the app
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_photos')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        
        file.save(file_path)
        
        # Save relative path for serving
        db_path = f"/static/uploads/profile_photos/{filename}"
        
        users_collection.update_one(
            {"email": current_user["email"]},
            {"$set": {"profile_photo_path": db_path}}
        )
        
        return jsonify({"status": True, "message": "Photo uploaded successfully", "path": db_path}), 200
        
    return jsonify({"status": False, "message": "Invalid file type. Allowed: png, jpg, jpeg, gif"}), 400
