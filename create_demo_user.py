#!/usr/bin/env python
"""Create a demo user for testing FarmersConnect"""
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='demo').first()
    if not user:
        user = User(username='demo', email='demo@farmersconnect.com')
        user.set_password('demo123')
        db.session.add(user)
        db.session.commit()
        print('✓ Demo user created successfully!')
        print('  Username: demo')
        print('  Password: demo123')
    else:
        print('✓ Demo user already exists')
