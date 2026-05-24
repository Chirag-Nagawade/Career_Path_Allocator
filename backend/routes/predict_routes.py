from flask import Blueprint, request, jsonify
import numpy as np
from datetime import datetime
import os
import sys

# Add the parent directory to Python path to import excel_processor
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from excel_processor import ExcelDataProcessor
from db import predictions_collection, users_collection, strength_analysis_collection, academic_marks_collection, psychometric_data_collection
from routes.auth_routes import token_required

predict_routes = Blueprint('predict_routes', __name__)

try:
    processor = ExcelDataProcessor()
    print("✅ ExcelDataProcessor initialized successfully!")
    print("✅ Models are ready for predictions!")
except Exception as e:
    print(f"❌ Error initializing ExcelDataProcessor: {e}")
    processor = None

# New unified endpoint called by our assessment.html frontend
@predict_routes.route('/predict/<standard>', methods=['POST'])
@token_required
def submit_assessment_and_predict(current_user, standard):
    if processor is None:
        return jsonify({'status': False, 'message': 'Prediction system not available'}), 500
        
    data = request.get_json()
    
    academic_raw = data.get('academic', {})
    academic = {k: float(v) if v else 0.0 for k, v in academic_raw.items()}
    psychometric = data.get('psychometric', {})
    
    # Save raw data
    academic_marks_collection.insert_one({"user_email": current_user['email'], "standard": standard, **academic})
    psychometric_data_collection.insert_one({"user_email": current_user['email'], "standard": standard, **psychometric})
    
    # Format data for prediction
    flat_data = {
        **academic,
        "analytical_thinking": int(psychometric.get('logical', 3)),
        "creativity": int(psychometric.get('creative', 3)),
        "problem_solving": int(psychometric.get('logical', 3)), # fallback
        "communication": int(psychometric.get('communication', 3)),
        "leadership": int(psychometric.get('leadership', 3)),
        "interest1": psychometric.get('interest1', 'Technology'),
        "interest2": psychometric.get('interest2', 'Science'),
        "interest3": psychometric.get('interest3', '')
    }
    
    if standard == '10th':
        prediction_result = run_10th_prediction(flat_data, current_user['email'])
        analysis_result = run_10th_analysis(flat_data, current_user['email'])
    elif standard == '12th':
        prediction_result = run_12th_prediction(flat_data, current_user['email'])
        analysis_result = run_12th_analysis(flat_data, current_user['email'])
    else:
        return jsonify({'status': False, 'message': 'Invalid standard'}), 400

    if prediction_result.get('error'):
        return jsonify({'status': False, 'message': prediction_result['error']}), 500
        
    # Mark user as assessment completed
    users_collection.update_one({"email": current_user['email']}, {"$set": {"assessment_completed": True}})

    return jsonify({
        'status': True,
        'message': 'Prediction successful'
    })


@predict_routes.route('/prediction', methods=['GET'])
@token_required
def get_prediction(current_user):
    # Get the latest prediction for the user
    pred = predictions_collection.find_one(
        {"user_email": current_user['email']}, 
        sort=[("timestamp", -1)]
    )
    if not pred:
        return jsonify({"status": False, "error": "No prediction found"})
        
    return jsonify({
        "status": True,
        "prediction": pred.get('top_careers', [])
    })

@predict_routes.route('/suggestions', methods=['GET'])
@token_required
def get_personalized_suggestions(current_user):
    """Return personalized suggestions using the refined 8-category recommendation engine."""
    email = current_user['email']
    acc = academic_marks_collection.find_one({"user_email": email}, sort=[("_id", -1)])
    psy = psychometric_data_collection.find_one({"user_email": email}, sort=[("_id", -1)])

    if not acc or not psy:
        return jsonify({"status": False, "error": "No assessment data found"})

    standard = acc.get('standard', '10th')
    
    # Extract marks
    if standard == '10th':
        marks = {k: float(v) for k, v in acc.items() if k in ['science', 'english', 'maths']}
    else:
        marks = {k: float(v) for k, v in acc.items() if k in ['physics', 'chemistry', 'maths', 'biology']}

    # Extract psychometric and interests
    psychometric = {
        'analytical_thinking': int(psy.get('logical') or psy.get('analytical_thinking') or 3),
        'creativity':          int(psy.get('creative') or psy.get('creativity') or 3),
        'leadership':          int(psy.get('leadership') or 3),
        'problem_solving':     int(psy.get('logical') or psy.get('problem_solving') or 3),
        'communication':       int(psy.get('communication') or 3),
    }
    interests = [psy.get('interest1', ''), psy.get('interest2', ''), psy.get('interest3', '')]
    user_interests = [i for i in interests if i]

    # Get refined recommended actions from processor
    recommended_actions = processor._get_recommended_actions(marks, psychometric, user_interests, standard)
    
    # Get personalized suggestions (the sentences like "SCIENCE STREAM PERFECT...")
    if standard == '10th':
        personalized_sentences = processor._generate_personalized_suggestions_10th(marks, psychometric, user_interests)
    else:
        personalized_sentences = processor._generate_personalized_suggestions_12th(marks, psychometric, user_interests)

    # Transform into the format expected by the frontend
    # strengths: Category A & B (excellent levels)
    # improvements: Category A & B (weak levels) & F
    # career_advice: Category C, D, E
    
    strengths = [a for a in recommended_actions if "excellent" in a.lower() or "remarkable strength" in a.lower()]
    improvements = [a for a in recommended_actions if "urgent attention" in a.lower() or "development needed" in a.lower() or "critical remediation" in a.lower()]
    career_advice = personalized_sentences + [a for a in recommended_actions if "recommended" in a.lower() or "perfect" in a.lower() or "profile" in a.lower()]

    return jsonify({
        "status": True,
        "suggestions": {
            "strengths":    strengths[:5] or ["Your academic focus is commendable. Maintain consistency across all subjects."],
            "improvements": improvements[:5] or ["No critical gaps identified. Focus on incremental improvements in all areas."],
            "career_advice": career_advice[:6],
            "action_plan": recommended_actions # Full 8-category plan
        }
    })

    return jsonify({
        "status": True,
        "suggestions": {
            "strengths":    strengths[:5],
            "improvements": improvements[:5],
            "career_advice": career_advice[:4],
        }
    })


@predict_routes.route('/strength-analysis', methods=['GET'])
@token_required
def get_strength_analysis(current_user):
    """Fetch user's latest analysis data from the specialized strength_analysis collection."""
    email = current_user['email']
    # Try specialized collection first
    strength_doc = strength_analysis_collection.find_one({"user_email": email}, sort=[("timestamp", -1)])
    
    if not strength_doc or 'academic' not in strength_doc or 'psychometric' not in strength_doc:
        # Fallback to raw data
        acc = academic_marks_collection.find_one({"user_email": email}, sort=[("_id", -1)])
        psy = psychometric_data_collection.find_one({"user_email": email}, sort=[("_id", -1)])
        if not acc or not psy:
            return jsonify({"status": False, "error": "No assessment data found"})
        
        strength_doc = {
            "academic": {k:v for k,v in acc.items() if k not in ['_id', 'user_email', 'timestamp']},
            "psychometric": {k:v for k,v in psy.items() if k not in ['_id', 'user_email', 'timestamp']}
        }

    # Map backend psychometric keys to frontend expectations
    # Frontend: logical, creative, communication, detail, leadership
    # Backend: analytical_thinking/problem_solving, creativity, communication, detail_orientation, leadership
    psy = strength_doc.get('psychometric', {})
    mapped_psy = {
        'logical':       psy.get('analytical_thinking', psy.get('problem_solving', psy.get('logical', 3))),
        'creative':      psy.get('creativity', psy.get('creative', 3)),
        'communication': psy.get('communication', 3),
        'detail':        psy.get('detail_orientation', psy.get('detail', 3)),
        'leadership':     psy.get('leadership', 3)
    }

    return jsonify({
        "status": True,
        "data": {
            "academic": strength_doc.get('academic', {}),
            "psychometric": mapped_psy
        }
    })

# --- Helper Functions ---

def run_10th_prediction(input_data, email):
    try:
        # Use analyze_user_strengths_10th for the new point-based scoring
        result = processor.analyze_user_strengths_10th(input_data)
        if result and result.get('success'):
            record = {
                "user_email": email,
                "standard": "10th",
                "predicted_career": result['matching_careers'][0]['career'] if result['matching_careers'] else "Undecided",
                "top_careers": result['matching_careers'], # Now contains match_score %
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            predictions_collection.insert_one(record)
            
            # Save strength analysis separately for the Performance Profile
            strength_record = {
                "user_email": email,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **result['strength_analysis']
            }
            strength_analysis_collection.insert_one(strength_record)
            
            return result
        return {"error": "Prediction failed internally"}
    except Exception as e:
        return {"error": str(e)}

def run_12th_prediction(input_data, email):
    try:
        # Use analyze_user_strengths_12th for point-based scoring
        result = processor.analyze_user_strengths_12th(input_data)
        if result and result.get('success'):
            record = {
                "user_email": email,
                "standard": "12th",
                "predicted_career": result['matching_careers'][0]['career'] if result['matching_careers'] else "Undecided",
                "top_careers": result['matching_careers'], # Now contains match_score %
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            predictions_collection.insert_one(record)
            
            # Save strength analysis
            strength_record = {
                "user_email": email,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **result['strength_analysis']
            }
            strength_analysis_collection.insert_one(strength_record)
            
            return result
        return {"error": "Prediction failed internally"}
    except Exception as e:
        return {"error": str(e)}

def run_10th_analysis(input_data, email):
    # Dummy wrapper to store analysis using the processor (kept for backwards compat)
    pass

def run_12th_analysis(input_data, email):
    pass