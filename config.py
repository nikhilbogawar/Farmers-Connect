"""
Configuration Management for FarmersConnect Application
Supports Development, Testing, and Production environments
"""

import os
from datetime import timedelta

class Config:
    """Base Configuration"""
    
    # ADD THIS (IMPORTANT FIX)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', False)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # FIXED: Use BASE_DIR here
    MODELS_FOLDER = os.path.join(BASE_DIR, 'models')
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///dev_database.db'
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/farmerconnect'
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing Configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration Dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config_dict.get(env, DevelopmentConfig)
