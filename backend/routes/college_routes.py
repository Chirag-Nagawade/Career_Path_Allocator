import os
import json
from flask import Blueprint, request, jsonify
from db import predictions_collection
from routes.auth_routes import token_required

college_routes = Blueprint('college_routes', __name__)

# Load colleges dataset
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
COLLEGES_FILE = os.path.join(DATA_DIR, 'colleges.json')

from utils.recommendation_utils import get_recommended_institutions, determine_stream

@college_routes.route('/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    try:
        city = request.args.get('city')
        if not city:
            return jsonify({'status': False, 'message': 'City is required'}), 400
            
        # Get user's latest prediction
        pred = predictions_collection.find_one(
            {"user_email": current_user['email']}, 
            sort=[("timestamp", -1)]
        )
        
        if not pred or not pred.get('top_careers'):
            return jsonify({'status': False, 'message': 'Complete your assessment first to get predictions.'}), 400
            
        top_careers = pred.get('top_careers')
        predicted_career = top_careers[0].get('career') or top_careers[0].get('Career_Name')
        target_stream = determine_stream(predicted_career)
        standard = pred.get('standard', '12th')
        
        # Get recommended institutions using common utility
        recommended = get_recommended_institutions(predicted_career, standard, city, limit=10)
        
        return jsonify({
            'status': True,
            'predicted_career': predicted_career,
            'mapped_stream': target_stream,
            'standard': standard,
            'recommendations': recommended
        })
    except Exception as e:
        import traceback
        with open('debug_error.log', 'w') as f:
            f.write(traceback.format_exc())
        return jsonify({'status': False, 'message': 'Internal Error: ' + str(e)}), 500
