#!/usr/bin/env python
"""Reset demo user credentials for testing"""
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check if demo user exists
    user = User.query.filter_by(username='demo').first()
    if user:
        print("✓ Demo user found")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        
        # Reset password
        user.set_password('demo123')
        db.session.commit()
        print("✓ Password reset to 'demo123'")
    else:
        print("✗ Demo user not found, creating new...")
        user = User(username='demo', email='demo@farmersconnect.com')
        user.set_password('demo123')
        db.session.add(user)
        db.session.commit()
        print("✓ Demo user created successfully")
        print("  Username: demo")
        print("  Password: demo123")
