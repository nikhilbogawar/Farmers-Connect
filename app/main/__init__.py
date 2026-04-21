"""
Main Blueprint
Dashboard and home page routes
"""
import os
from werkzeug.utils import secure_filename
from app.predictions.disease_logic import predict_disease  # The file you created
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import db, PredictionHistory
from sqlalchemy import desc
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User Dashboard"""
    try:
        # Get recent predictions for the current user
        recent_predictions = PredictionHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(PredictionHistory.created_at)).limit(5).all()
        
        # Count predictions by type
        stats = {
            'total_predictions': PredictionHistory.query.filter_by(user_id=current_user.id).count(),
            'crop_predictions': PredictionHistory.query.filter_by(
                user_id=current_user.id,
                prediction_type='crop'
            ).count(),
            'fertilizer_predictions': PredictionHistory.query.filter_by(
                user_id=current_user.id,
                prediction_type='fertilizer'
            ).count(),
            'disease_predictions': PredictionHistory.query.filter_by(
                user_id=current_user.id,
                prediction_type='disease'
            ).count(),
        }
        
        logger.info(f"Dashboard accessed by user: {current_user.username}")
        
        return render_template(
            'dashboard.html',
            user=current_user,
            recent_predictions=recent_predictions,
            stats=stats
        )
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        return render_template('dashboard.html', error=str(e)), 500


@main_bp.route('/history')
@login_required
def prediction_history():
    """View prediction history"""
    try:
        # Get all predictions for current user with pagination
        page = request.args.get('page', 1, type=int)
        predictions = PredictionHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(desc(PredictionHistory.created_at)).paginate(page=page, per_page=10)
        
        logger.info(f"History accessed by user: {current_user.username}")
        
        return render_template('history.html', predictions=predictions)
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return render_template('history.html', error=str(e)), 500

@main_bp.route('/predict/disease', methods=['GET', 'POST'])
def disease():
    if request.method == 'POST':
        file = request.files.get('image')

        if file and file.filename != "":
            import os
            upload_path = os.path.join('static/uploads', file.filename)
            file.save(upload_path)

            # 🔥 run model
            result = predict_disease(upload_path)

            print("PREDICTION:", result)  # debug

            return render_template(
                'disease.html',
                prediction={'disease': result}
            )

    return render_template('disease.html', prediction=None)