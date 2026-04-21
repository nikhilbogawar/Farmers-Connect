"""
Flask Application Factory and Initialization
FarmersConnect - Agricultural AI Assistant
"""

import logging
import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import get_config
from app.models import db, User

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask extensions
login_manager = LoginManager()


def create_app(config_name=None):
    """
    Application Factory Function
    
    Args:
        config_name (str): Configuration environment name
    
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Get configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config = get_config(config_name)
    
    # Create Flask app with correct template and static folders
    template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(config)
    
    # Validate production database if in production
    if config_name == 'production' and 'DATABASE_URL' not in os.environ:
        logger.warning('DATABASE_URL not set in production. Using default SQLite. Please set DATABASE_URL for PostgreSQL.')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Setup login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID"""
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.predictions import predictions_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(predictions_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        logger.warning(f"404 error: {error}")
        return {'error': 'Page not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"500 error: {error}")
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    # Ensure upload folder exists
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    
    logger.info(f"FarmersConnect application created - Environment: {config_name}")
    
    return app
