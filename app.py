"""
FarmersConnect - Agricultural AI Assistant
Main Application Entry Point

Usage:
    python app.py
    
Set environment variables:
    FLASK_ENV=development (or production)
    SECRET_KEY=your-secret-key
    DATABASE_URL=postgresql://user:pass@host/db (for production)
"""

import os
import logging
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, PredictionHistory

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = create_app()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.shell_context_processor
def make_shell_context():
    """Add objects to shell context for flask shell"""
    return {
        'db': db,
        'User': User,
        'PredictionHistory': PredictionHistory
    }


@app.before_request
def before_request():
    """Execute before each request"""
    pass


@app.after_request
def after_request(response):
    """Execute after each request"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    logger.info('Database initialized.')
    print('Database initialized.')


@app.cli.command()
def create_demo_user():
    """Create a demo user for testing."""
    try:
        # Check if user already exists
        demo_user = User.query.filter_by(username='demo_farmer').first()
        
        if demo_user:
            print('Demo user already exists.')
            logger.info('Demo user already exists.')
            return
        
        # Create demo user
        user = User(
            username='demo_farmer',
            email='demo@farmerconnect.local'
        )
        user.set_password('demo_password_123')
        
        db.session.add(user)
        db.session.commit()
        
        print('Demo user created successfully!')
        print('Username: demo_farmer')
        print('Password: demo_password_123')
        logger.info('Demo user created')
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating demo user: {str(e)}')
        print(f'Error: {str(e)}')


if __name__ == '__main__':
    # Get configuration
    env = os.environ.get('FLASK_ENV', 'development')
    debug_mode = (env == 'development')
    
    logger.info(f"Starting FarmersConnect - Environment: {env}")
    logger.info(f"Debug Mode: {debug_mode}")
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode
    )
