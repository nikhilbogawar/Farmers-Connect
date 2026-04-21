#!/bin/bash

# FarmersConnect Quick Setup Script for Linux/macOS
# This script automates the initial setup of the application

echo ""
echo "========================================"
echo "  FarmersConnect Setup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://www.python.org/"
    exit 1
fi

echo "[✓] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "[✓] Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "[✓] Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip wheel setuptools > /dev/null 2>&1
echo "[✓] pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Installation failed. Please check your internet connection."
    exit 1
fi
echo "[✓] Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ -f ".env" ]; then
    echo ".env file already exists"
else
    echo "Creating .env file..."
    cp .env.example .env
    echo "[✓] .env file created (please edit with your settings)"
fi
echo ""

# Initialize database
echo "Initializing database..."
python app.py init-db
echo "[✓] Database initialized"
echo ""

# Create demo user
echo "Creating demo user..."
python app.py create-demo-user
echo "[✓] Demo user setup complete"
echo ""

echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the application, run:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "The application will be available at:"
echo "  http://localhost:5000"
echo ""
echo "Demo Credentials:"
echo "  Username: demo_farmer"
echo "  Password: demo_password_123"
echo ""
