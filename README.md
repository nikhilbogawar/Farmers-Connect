# FarmersConnect - Agricultural AI Assistant

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-green)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)](https://flask.palletsprojects.com/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**FarmersConnect** is a production-ready full-stack web application that empowers farmers with AI-powered agricultural recommendations. It provides intelligent suggestions for crop selection, fertilizer recommendations, and plant disease detection.

## 🌾 Features

### Core Features
- **🌱 Crop Recommendation**: AI-powered crop suggestions based on soil nutrients and climate parameters
- **🧪 Fertilizer Suggestion**: Personalized fertilizer recommendations based on soil type and crop requirements
- **🦠 Plant Disease Detection**: AI-powered disease identification from plant/leaf images
- **👤 Authentication System**: Secure user registration and login with password hashing
- **📊 Dashboard**: Comprehensive user dashboard with statistics and prediction history
- **🌍 Multi-language Support**: Google Translate integration for global accessibility

### Technical Features
- **Flask Blueprints**: Modular and scalable application architecture
- **SQLAlchemy ORM**: Database abstraction layer with support for SQLite and PostgreSQL
- **Machine Learning**: Pre-trained ML models for predictions (RandomForest, CNN)
- **Modern UI**: Bootstrap 5 with custom CSS for responsive design
- **Cloud-Ready**: Deployment-optimized for Render, Railway, AWS, and PythonAnywhere

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (venv)
- PostgreSQL (for production) or SQLite (for development)

## 🚀 Local Setup & Development

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/FarmersConnect.git
cd FarmersConnect
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
# Create .env file from example
cp .env.example .env

# Edit .env and add your secret key
# Generate a strong secret key:
# python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize Database
```bash
# Create database tables
python app.py init-db

# Create demo user (optional)
python app.py create-demo-user
```

### 6. Train or Add ML Models (required for useful predictions)

By default the repository ships with *placeholder* models.  You must
provide real classifiers in the `models/` folder for the app to return
meaningful results.

Two options:

1. **Run the training script**
   - Prepare CSV files in a new `data/` directory (`crop_training.csv`
     and `fertilizer_training.csv`).  See the comments at the top of
     `train_models.py` for column formats.
   - Execute:
     ```bash
     python train_models.py
     ```
   - The script writes `crop_model.pkl` and `fertilizer_model.pkl` into
     `models/`.

2. **Copy pre‑trained models**
   - If you already have `.pkl`/`.h5` files, simply place them under
     `models/` (e.g. `models/disease_model.h5`).
   - The application will load them automatically; if a dataset is
     present under `models/disease_dataset/` the disease model will train
     itself on first use.

After training or copying, restart the Flask server; predictions will
now vary according to the input data.

### 7. Run Development Server
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 7. Demo Credentials
```
Username: demo_farmer
Password: demo_password_123
```

## 📁 Project Structure

```
FarmersConnect/
│
├── app.py                          # Flask application entry point
├── config.py                       # Configuration management
├── ml_utils.py                     # ML model utilities and predictions
├── requirements.txt                # Python dependencies
├── Procfile                        # Deployment configuration
├── runtime.txt                     # Python version specification
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Documentation
│
├── app/                            # Flask application package
│   ├── __init__.py                 # App factory
│   ├── models.py                   # Database models (User, PredictionHistory)
│   │
│   ├── auth/                       # Authentication blueprint
│   │   └── __init__.py             # Auth routes (login, signup, logout)
│   │
│   ├── main/                       # Main blueprint
│   │   └── __init__.py             # Dashboard and main routes
│   │
│   └── predictions/                # Predictions blueprint
│       └── __init__.py             # Prediction routes (crop, fertilizer, disease)
│
├── models/                         # Pre-trained ML models
│   ├── crop_model.pkl              # RandomForest crop model
│   ├── fertilizer_model.pkl        # Fertilizer recommendation model
│   └── disease_model.h5            # CNN disease detection model
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Main stylesheet
│   ├── js/
│   │   └── script.js               # JavaScript utilities
│   └── uploads/                    # User uploaded images
│
├── templates/                      # Jinja2 templates
│   ├── base.html                   # Base template with navigation
│   ├── login.html                  # Login page
│   ├── signup.html                 # Registration page
│   ├── dashboard.html              # User dashboard
│   ├── crop.html                   # Crop recommendation page
│   ├── fertilizer.html             # Fertilizer suggestion page
│   └── disease.html                # Disease detection page
│
└── instance/                       # Instance folder (runtime)
    └── database.db                 # SQLite database (development)
```

## 🛠 Technology Stack

### Backend
- **Flask 2.3.3**: Lightweight Python web framework
- **SQLAlchemy 3.0.5**: ORM for database operations
- **Werkzeug 2.3.7**: Security utilities including password hashing
- **Python-dotenv 1.0.0**: Environment variable management

### Frontend
- **HTML5**: Semantic markup
- **Bootstrap 5.3**: Responsive CSS framework
- **CSS3**: Custom styling with gradients and animations
- **JavaScript (Vanilla)**: Interactivity without jQuery
- **Font Awesome 6.4**: Icon library
- **Google Translate**: Multi-language support

### Database
- **SQLite**: Development (fast, no setup required)
- **PostgreSQL**: Production (scalable, enterprise-ready)

### Machine Learning
- **scikit-learn 1.3.0**: RandomForest models
- **TensorFlow/Keras 2.13.0**: Deep learning for CNN models
- **NumPy 1.24.3**: Numerical computing
- **Pillow 10.0.0**: Image processing

### Deployment
- **Gunicorn 21.2.0**: WSGI application server
- **Flask-Login**: Session management
- **psycopg2-binary**: PostgreSQL adapter

## 🎯 Core Functionalities

### 1. Crop Recommendation
```
Input: Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall
Output: Recommended crop for farming
Model: Pre-trained RandomForest classifier
```

### 2. Fertilizer Suggestion
```
Input: Soil Type, Crop Type, Current NPK levels
Output: Recommended fertilizer composition
Model: Pre-trained classifier
Example Output: NPK 20-10-10, NPK 15-15-15
```

### 3. Plant Disease Detection
```
Input: Plant/Leaf image (PNG, JPG, JPEG, GIF)
Output: Disease name + treatment recommendations
Model: Pre-trained CNN (TensorFlow/Keras)
Supported: Early Blight, Late Blight, Powdery Mildew, Healthy
```

## 🔐 Security Features

- **Password Hashing**: PBKDF2-SHA256 via Werkzeug
- **Session Management**: Secure cookie-based sessions
- **CSRF Protection**: Available with Flask-WTF integration
- **Environment Variables**: Sensitive data management
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries

## 📊 Database Models

### User Model
```python
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash (PBKDF2)
- created_at
- updated_at
```

### PredictionHistory Model
```python
- id (Primary Key)
- user_id (Foreign Key)
- prediction_type (crop/fertilizer/disease)
- input_data (JSON)
- prediction_result
- confidence (0-1)
- created_at
```

## ☁️ Cloud Deployment Guides

### Deploy on Render
1. Push code to GitHub repository
2. Connect GitHub account to Render
3. Create new Web Service from repository
4. Configure environment variables:
   ```
   FLASK_ENV=production
   SECRET_KEY=<your-secret-key>
   DATABASE_URL=<postgresql-url>
   ```
5. Deploy with Python 3.11 runtime

### Deploy on Railway
1. Install Railway CLI: `npm i -g @railway/cli`
2. Initialize Railway: `railway init`
3. Set environment variables: `railway variables set`
4. Deploy: `railway up`

### Deploy on AWS (EC2 + RDS)
1. Create EC2 instance (Ubuntu 22.04)
2. Create RDS PostgreSQL database
3. SSH into EC2 and clone repository
4. Install dependencies and configure .env
5. Run with Gunicorn: `gunicorn --bind 0.0.0.0:5000 app:app`
6. Use Nginx as reverse proxy

### Deploy on PythonAnywhere
1. Create new account on PythonAnywhere
2. Upload code via Web interface or Git
3. Create virtual environment
4. Configure WSGI file to point to Flask app
5. Set environment variables in Web app settings
6. Reload web app to apply changes

## 🔧 Environment Variables

```env
# Critical for Production
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@host:5432/farmerconnect

# Optional
SESSION_COOKIE_SECURE=True
LOG_LEVEL=INFO
PORT=5000
```

## 📈 Performance Optimization

- **Model Caching**: ML models are cached in memory after first use
- **Database Indexing**: User_id and created_at indexed for faster queries
- **Lazy Loading**: Relationships load only when accessed
- **Static File Compression**: CSS and JS minified in production
- **Image Optimization**: Uploaded images resized to 224x224 for consistency

## 🐛 Troubleshooting

### Issue: Models not loading
**Solution**: Placeholder models provide fallback predictions. Place actual .pkl and .h5 files in `models/` directory.

### Issue: Database locked (SQLite)
**Solution**: Use PostgreSQL for production. SQLite has limitations for concurrent access.

### Issue: Secret key error
**Solution**: Generate strong secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Issue: Module not found
**Solution**: Ensure virtual environment is activated and all packages installed:
```bash
pip install -r requirements.txt
```

## 📝 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Main
- `GET /` - Home page
- `GET /dashboard` - User dashboard

### Predictions
- `GET/POST /predict/crop` - Crop recommendation
- `GET/POST /predict/fertilizer` - Fertilizer suggestion
- `GET/POST /predict/disease` - Disease detection

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🌟 Future Enhancements

- [ ] Email notifications for predictions
- [ ] Mobile app (React Native/Flutter)
- [ ] Weather API integration
- [ ] Real-time soil sensor integration
- [ ] Community forum for farmers
- [ ] Multilingual documentation
- [ ] Video tutorials
- [ ] SMS-based recommendations

## 📧 Contact & Support

- **Email**: support@farmerconnect.local
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: See docs/ folder for detailed guides

## 🙏 Acknowledgments

- Bootstrap team for excellent UI framework
- scikit-learn and TensorFlow communities
- Flask ecosystem contributors
- Agricultural extension services for knowledge

---

**FarmersConnect** - Bringing AI-powered agriculture to every farmer! 🌾🤖
#   F a r m e r s - C o n n e c t  
 