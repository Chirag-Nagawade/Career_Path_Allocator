from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from db import users_collection

auth_routes = Blueprint('auth_routes', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # JWT is passed in the request header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = users_collection.find_one({'email': data['email']})
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        # returns the current logged in users context to the routes
        return f(current_user, *args, **kwargs)

    return decorated

# ---------------- SIGNUP ----------------
@auth_routes.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if not all([full_name, email, password, confirm_password]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"status": "error", "message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    
    user_data = {
        "full_name": full_name,
        "email": email,
        "password_hash": hashed_password,
        "role": "user",
        "profile_photo_path": None,
        "assessment_completed": False,
        "created_at": datetime.datetime.utcnow()
    }
    
    users_collection.insert_one(user_data)
    
    # Generate token automatically upon signup (optional)
    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "status": "success", 
        "message": "Signup successful!",
        "token": token,
        "user": {
            "full_name": full_name,
            "email": email,
            "role": "user"
        }
    }), 201

# ---------------- LOGIN ----------------
@auth_routes.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"status": "error", "message": "Missing email or password"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"status": "error", "message": "Email not found"}), 404

    # The existing database might have old bcrypt passwords, this handles only Werkzeug hash
    # For a real migration we'd handle both, but assuming we are starting fresh or recreating users.
    if "password_hash" not in user:
        return jsonify({"status": "error", "message": "Account must be recreated for new auth system"}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"status": "error", "message": "Incorrect password"}), 401

    token = jwt.encode({
        'email': user['email'],
        'role': user.get('role', 'user'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "token": token,
        "user": {
            "full_name": user.get("full_name", user.get("name")),
            "email": user["email"],
            "role": user.get("role", "user"),
            "assessment_completed": user.get("assessment_completed", False),
            "profile_photo_path": user.get("profile_photo_path")
        }
    }), 200
