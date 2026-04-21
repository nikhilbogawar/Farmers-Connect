"""
Predictions Blueprint
Routes for crop, fertilizer, and disease predictions
"""

import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, PredictionHistory
import ml_utils
import logging

logger = logging.getLogger(__name__)

predictions_bp = Blueprint('predictions', __name__, url_prefix='/predict')


def allowed_file(filename):
    """Check if file is allowed"""
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def wants_json():
    """Detect whether the client expects a JSON response."""
    accept_header = request.headers.get('Accept', '')
    return request.is_json or 'application/json' in accept_header.lower()


def api_response(data=None, message=None, error=None, status=200):
    """Build a consistent API response payload."""
    payload = {
        'success': error is None,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    if error is not None:
        payload.update({
            'error': error,
            'status': status
        })
        return jsonify(payload), status

    if message is not None:
        payload['message'] = message

    if isinstance(data, dict):
        payload.update(data)
    else:
        payload['data'] = data

    return jsonify(payload), status


@predictions_bp.route('/crop', methods=['GET', 'POST'])
@login_required
def crop():
    """Crop Recommendation Page and API"""
    
    if request.method == 'POST':
        try:
            payload = request.get_json(silent=True) or {}
            if payload:
                nitrogen = float(payload.get('nitrogen', 0))
                phosphorus = float(payload.get('phosphorus', 0))
                potassium = float(payload.get('potassium', 0))
                temperature = float(payload.get('temperature', 0))
                humidity = float(payload.get('humidity', 0))
                ph = float(payload.get('ph', 0))
                rainfall = float(payload.get('rainfall', 0))
            else:
                nitrogen = float(request.form.get('nitrogen', 0))
                phosphorus = float(request.form.get('phosphorus', 0))
                potassium = float(request.form.get('potassium', 0))
                temperature = float(request.form.get('temperature', 0))
                humidity = float(request.form.get('humidity', 0))
                ph = float(request.form.get('ph', 0))
                rainfall = float(request.form.get('rainfall', 0))
            
            if not all([
                nitrogen >= 0,
                phosphorus >= 0,
                potassium >= 0,
                temperature >= -50,
                humidity >= 0,
                humidity <= 100,
                ph >= 0,
                ph <= 14,
                rainfall >= 0
            ]):
                error_msg = 'Please enter valid input values.'
                if wants_json():
                    return api_response(error=error_msg, status=400)
                flash(error_msg, 'warning')
                return redirect(url_for('predictions.crop'))
            
            result = ml_utils.predict_crop(
                nitrogen, phosphorus, potassium,
                temperature, humidity, ph, rainfall
            )
            
            input_data = {
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'temperature': temperature,
                'humidity': humidity,
                'ph': ph,
                'rainfall': rainfall
            }
            
            prediction = PredictionHistory(
                user_id=current_user.id,
                prediction_type='crop',
                input_data=input_data,
                prediction_result=result.get('crop', ''),
                confidence=result.get('confidence')
            )
            
            db.session.add(prediction)
            db.session.commit()
            logger.info(f"Crop prediction made for user {current_user.username}: {result.get('crop')}")
            
            if wants_json():
                return api_response(data=result, message='Crop prediction successful')
            
            return render_template(
                'crop.html',
                prediction=result,
                inputs=input_data
            )
        
        except ValueError:
            error_msg = 'Please enter valid numeric values.'
            logger.warning(f"Invalid input in crop prediction for user {current_user.username}")
            if wants_json():
                return api_response(error=error_msg, status=400)
            flash(error_msg, 'danger')
            return redirect(url_for('predictions.crop'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Crop prediction error: {str(e)}")
            if wants_json():
                return api_response(error=f'Error: {str(e)}', status=500)
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('predictions.crop'))
    
    return render_template('crop.html')


@predictions_bp.route('/fertilizer', methods=['GET', 'POST'])
@login_required
def fertilizer():
    """Fertilizer Recommendation Page and API"""
    
    if request.method == 'POST':
        try:
            payload = request.get_json(silent=True) or {}
            if payload:
                soil_type = str(payload.get('soil_type', '')).strip()
                crop_type = str(payload.get('crop_type', '')).strip()
                nitrogen = float(payload.get('nitrogen', 0))
                phosphorus = float(payload.get('phosphorus', 0))
                potassium = float(payload.get('potassium', 0))
            else:
                soil_type = request.form.get('soil_type', '').strip()
                crop_type = request.form.get('crop_type', '').strip()
                nitrogen = float(request.form.get('nitrogen', 0))
                phosphorus = float(request.form.get('phosphorus', 0))
                potassium = float(request.form.get('potassium', 0))
            
            if not all([soil_type, crop_type, nitrogen >= 0, phosphorus >= 0, potassium >= 0]):
                error_msg = 'Please fill all fields with valid values.'
                if wants_json():
                    return api_response(error=error_msg, status=400)
                flash(error_msg, 'warning')
                return redirect(url_for('predictions.fertilizer'))
            
            result = ml_utils.predict_fertilizer(
                soil_type, crop_type, nitrogen, phosphorus, potassium
            )
            
            input_data = {
                'soil_type': soil_type,
                'crop_type': crop_type,
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium
            }
            
            prediction = PredictionHistory(
                user_id=current_user.id,
                prediction_type='fertilizer',
                input_data=input_data,
                prediction_result=result.get('fertilizer', ''),
                confidence=None
            )
            
            db.session.add(prediction)
            db.session.commit()
            logger.info(f"Fertilizer prediction made for user {current_user.username}: {result.get('fertilizer')}")
            
            if wants_json():
                return api_response(data=result, message='Fertilizer recommendation successful')
            
            return render_template(
                'fertilizer.html',
                prediction=result,
                inputs=input_data
            )
        
        except ValueError:
            error_msg = 'Please enter valid values.'
            logger.warning(f"Invalid input in fertilizer prediction for user {current_user.username}")
            if wants_json():
                return api_response(error=error_msg, status=400)
            flash(error_msg, 'danger')
            return redirect(url_for('predictions.fertilizer'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Fertilizer prediction error: {str(e)}")
            if wants_json():
                return api_response(error=f'Error: {str(e)}', status=500)
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('predictions.fertilizer'))
    
    return render_template('fertilizer.html')


@predictions_bp.route('/disease', methods=['GET', 'POST'])
@login_required
def disease():
    """Plant Disease Detection Page and API"""
    
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                error_msg = 'No image file selected.'
                if wants_json():
                    return api_response(error=error_msg, status=400)
                flash(error_msg, 'warning')
                return redirect(url_for('predictions.disease'))
            
            file = request.files['image']
            
            if file.filename == '':
                error_msg = 'No image file selected.'
                if wants_json():
                    return api_response(error=error_msg, status=400)
                flash(error_msg, 'warning')
                return redirect(url_for('predictions.disease'))
            
            if not allowed_file(file.filename):
                error_msg = 'Invalid file type. Please upload PNG, JPG, JPEG, or GIF.'
                if wants_json():
                    return api_response(error=error_msg, status=400)
                flash(error_msg, 'danger')
                return redirect(url_for('predictions.disease'))
            
            uploads_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(uploads_folder, exist_ok=True)
            
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            import time
            filename = f"{int(time.time())}_{filename}"
            
            filepath = os.path.join(uploads_folder, filename)
            file.save(filepath)
            
            result = ml_utils.predict_disease(filepath)
            
            input_data = {
                'image_filename': filename,
                'image_path': filepath
            }
            
            prediction = PredictionHistory(
                user_id=current_user.id,
                prediction_type='disease',
                input_data=input_data,
                prediction_result=result.get('disease', ''),
                confidence=result.get('confidence')
            )
            
            db.session.add(prediction)
            db.session.commit()
            logger.info(f"Disease prediction made for user {current_user.username}: {result.get('disease')}")
            
            if wants_json():
                return api_response(data=result, message='Disease detection successful')
            
            return render_template(
                'disease.html',
                prediction=result,
                image_filename=filename
            )
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Disease prediction error: {str(e)}")
            if wants_json():
                return api_response(error=f'Error during prediction: {str(e)}', status=500)
            flash(f'Error during prediction: {str(e)}', 'danger')
            return redirect(url_for('predictions.disease'))
    
    return render_template('disease.html')
