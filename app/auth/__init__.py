"""
Authentication Blueprint
Handles user registration, login, and logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import db, User
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User Registration Route"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Basic validation
            if not all([username, email, password, confirm_password]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('auth.signup'))
            
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('auth.signup'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return redirect(url_for('auth.signup'))
            
            if len(username) < 3:
                flash('Username must be at least 3 characters long.', 'danger')
                return redirect(url_for('auth.signup'))
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose a different one.', 'warning')
                return redirect(url_for('auth.signup'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered. Please use a different email or login.', 'warning')
                return redirect(url_for('auth.signup'))
            
            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"New user registered: {username}")
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.signup'))
    
    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User Login Route"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)
            
            if not username or not password:
                flash('Username and password are required.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Find user
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                logger.info(f"User logged in: {username}")
                flash(f'Welcome back, {username}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
            else:
                logger.warning(f"Failed login attempt for: {username}")
                flash('Invalid username or password.', 'danger')
                return redirect(url_for('auth.login'))
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """User Logout Route"""
    username = current_user.username if current_user.is_authenticated else 'User'
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out. See you soon!', 'info')
    return redirect(url_for('auth.login'))
