import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from routes.predict_routes import predict_routes
from routes.auth_routes import auth_routes
from routes.profile_routes import profile_routes
from routes.admin_routes import admin_routes
from routes.report_routes import report_routes
from routes.college_routes import college_routes

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# Settings config
app.config['JWT_SECRET_KEY'] = 'margintel-super-secret-key-2026' # Should use env var in prod
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # 5 MB max for uploads

# Ensure upload directory exists
os.makedirs(os.path.join(app.root_path, 'static', 'uploads', 'profile_photos'), exist_ok=True)

# Register routes
app.register_blueprint(predict_routes, url_prefix="/")
app.register_blueprint(auth_routes, url_prefix="/auth")
app.register_blueprint(profile_routes, url_prefix="/profile")
app.register_blueprint(admin_routes, url_prefix="/admin")
app.register_blueprint(report_routes, url_prefix="/reports")
app.register_blueprint(college_routes, url_prefix="/api/colleges")

# Configure frontend directory (Absolute path)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "public"))

@app.route('/')
@app.route('/landing')
def landing():
    return send_from_directory(FRONTEND_DIR, 'landing.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory(FRONTEND_DIR, 'style.css', mimetype='text/css')

@app.route('/app.js')
def serve_js():
    return send_from_directory(FRONTEND_DIR, 'app.js', mimetype='application/javascript')

@app.route('/<path:filename>')
def serve_public(filename):
    # If the file has an extension, serve it directly from frontend dir
    if '.' in filename:
        return send_from_directory(FRONTEND_DIR, filename)
    # Otherwise, assume it's an HTML page in the frontend dir
    return send_from_directory(FRONTEND_DIR, f"{filename}.html")

@app.route('/api/status')
def api_status():
    return jsonify({
        "message": "MargIntel API endpoint is running.",
        "status": "running"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)