# FarmersConnect API Documentation

## Overview

FarmersConnect provides a RESTful API for agricultural predictions and user management. All endpoints follow REST conventions and return JSON responses.

## Base URL

**Development**: `http://localhost:5000`
**Production**: `https://farmerconnect.onrender.com` (example)

## Authentication

The application uses session-based authentication. Users must:
1. Register via `/auth/signup`
2. Login via `/auth/login`
3. Include session cookies in subsequent requests

All prediction endpoints require authentication (`@login_required`).

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "timestamp": "2024-02-22T10:30:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": "Error message",
  "status": 400,
  "timestamp": "2024-02-22T10:30:00Z"
}
```

## Endpoints

### Authentication Endpoints

#### 1. User Signup
```
POST /auth/signup
Content-Type: application/x-www-form-urlencoded
```

**Request Parameters:**
- `username` (string, required): 3-80 characters, alphanumeric
- `email` (string, required): Valid email address
- `password` (string, required): Minimum 6 characters
- `confirm_password` (string, required): Must match password

**Response (Success - 302 Redirect):**
```
Redirects to /auth/login
Flash: "Account created successfully! Please log in."
```

**Response (Error):**
```json
{
  "error": "Username already exists",
  "status": 409
}
```

**Error Codes:**
- `400`: Missing or invalid fields
- `409`: Username or email already exists
- `500`: Server error

**Example:**
```bash
curl -X POST http://localhost:5000/auth/signup \
  -d "username=farmer_john&email=john@farm.local&password=secure123&confirm_password=secure123"
```

---

#### 2. User Login
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

**Request Parameters:**
- `username` (string, required): Registered username
- `password` (string, required): Account password
- `remember` (boolean, optional): Remember for 7 days

**Response (Success - 302 Redirect):**
```
Redirects to /dashboard
Flash: "Welcome back, farmer_john!"
Session cookie set with 7-day lifetime
```

**Response (Error - 401):**
```json
{
  "error": "Invalid username or password",
  "status": 401
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -d "username=demo_farmer&password=demo_password_123&remember=on" \
  -c cookies.txt
```

---

#### 3. User Logout
```
GET /auth/logout
```

**Authentication**: Required (session cookie)

**Response (302 Redirect):**
```
Redirects to /auth/login
Flash: "You have been logged out. See you soon!"
```

**Example:**
```bash
curl -X GET http://localhost:5000/auth/logout \
  -b cookies.txt
```

---

### Dashboard Endpoints

#### 1. Dashboard
```
GET /dashboard
```

**Authentication**: Required

**Response (200 OK - HTML):**
Returns the dashboard page with:
- User statistics (total predictions, by type)
- Recent predictions (last 5)
- Feature cards for each tool

**Example:**
```bash
curl -X GET http://localhost:5000/dashboard \
  -b cookies.txt
```

---

#### 2. Prediction History
```
GET /history
```

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)

**Authentication**: Required

**Response (200 OK - HTML):**
Returns paginated prediction history with:
- All user predictions
- 10 predictions per page
- Type, result, confidence, timestamp

**Example:**
```bash
curl -X GET "http://localhost:5000/history?page=1" \
  -b cookies.txt
```

---

### Prediction Endpoints

#### 1. Crop Recommendation
```
POST /predict/crop
Content-Type: application/x-www-form-urlencoded
```

**Authentication**: Required

**Request Parameters:**
| Parameter | Type | Range | Unit | Description |
|-----------|------|-------|------|-------------|
| nitrogen | float | 0-200 | mg/kg | Soil nitrogen level |
| phosphorus | float | 0-200 | mg/kg | Soil phosphorus level |
| potassium | float | 0-200 | mg/kg | Soil potassium level |
| temperature | float | -50 to 60 | °C | Average temperature |
| humidity | float | 0-100 | % | Air humidity |
| ph | float | 0-14 | - | Soil pH value |
| rainfall | float | 0-10000 | mm | Annual rainfall |

**Response (200 OK - HTML):**
```html
<!-- Result page showing:
- Predicted crop
- Confidence score (0-100%)
- Recommendation details
- Option to try another prediction
-->
```

**Database Recording:**
```python
PredictionHistory(
  user_id=current_user.id,
  prediction_type='crop',
  input_data={...},
  prediction_result='Wheat',
  confidence=0.87
)
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/predict/crop \
  -d "nitrogen=40&phosphorus=30&potassium=40&temperature=25&humidity=60&ph=6.5&rainfall=1200" \
  -b cookies.txt
```

**Example Response Data:**
```json
{
  "crop": "Wheat",
  "confidence": 0.87,
  "success": true,
  "message": "Prediction successful"
}
```

---

#### 2. Fertilizer Recommendation
```
POST /predict/fertilizer
Content-Type: application/x-www-form-urlencoded
```

**Authentication**: Required

**Request Parameters:**
| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| soil_type | string | loamy, sandy, clayey | Soil classification |
| crop_type | string | rice, wheat, corn, potato, cotton, sugarcane, vegetables | Crop to cultivate |
| nitrogen | float | 0-200 | Current nitrogen level |
| phosphorus | float | 0-200 | Current phosphorus level |
| potassium | float | 0-200 | Current potassium level |

**Response (200 OK - HTML):**
Returns recommendation page with:
- Recommended fertilizer (e.g., "NPK 20-10-10")
- Applied amount guidance
- Application schedule

**Database Recording:**
```python
PredictionHistory(
  user_id=current_user.id,
  prediction_type='fertilizer',
  input_data={...},
  prediction_result='NPK 20-10-10',
  confidence=None
)
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/predict/fertilizer \
  -d "soil_type=loamy&crop_type=wheat&nitrogen=20&phosphorus=15&potassium=30" \
  -b cookies.txt
```

**Example Response Data:**
```json
{
  "fertilizer": "NPK 20-10-10",
  "description": "Recommended based on soil and crop analysis",
  "success": true,
  "message": "Recommendation successful"
}
```

---

#### 3. Plant Disease Detection
```
POST /predict/disease
Content-Type: multipart/form-data
```

**Authentication**: Required

**Request Parameters:**
- `image` (file, required): Plant/leaf image
  - Formats: PNG, JPG, JPEG, GIF
  - Max size: 16 MB
  - Recommended: 224x224 pixels or larger

**Response (200 OK - HTML):**
Returns disease detection page with:
- Disease name and confidence
- Treatment recommendations
- Prevention tips

**Image Processing:**
1. Validate file type and size
2. Save to `static/uploads/`
3. Resize to 224x224
4. Normalize pixel values
5. Feed to CNN model
6. Return top prediction

**Database Recording:**
```python
PredictionHistory(
  user_id=current_user.id,
  prediction_type='disease',
  input_data={'image_filename': '...'},
  prediction_result='Early Blight',
  confidence=0.94
)
```

**Supported Diseases:**
- Early Blight
- Late Blight
- Powdery Mildew
- Healthy Leaf

**Example Request (cURL):**
```bash
curl -X POST http://localhost:5000/predict/disease \
  -F "image=@leaf.jpg" \
  -b cookies.txt
```

**Example Response Data:**
```json
{
  "disease": "Early Blight",
  "treatment": "Use copper or mancozeb fungicide. Remove infected leaves.",
  "confidence": 0.94,
  "success": true,
  "message": "Disease detection successful"
}
```

---

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "success": false,
  "error": "Please enter valid numeric values",
  "status": 400
}
```

**401 Unauthorized:**
```json
{
  "success": false,
  "error": "Please log in to access this page",
  "status": 401
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": "Page not found",
  "status": 404
}
```

**413 Payload Too Large:**
```json
{
  "success": false,
  "error": "File size exceeds 16MB limit",
  "status": 413
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Internal server error",
  "status": 500
}
```

---

## Rate Limiting

Currently implemented at Nginx level when using Docker:
- General endpoints: 10 requests/second
- API endpoints: 30 requests/second
- Burst allowed: 20-50 requests

Future implementation: Add Flask-Limiter for application-level control.

---

## Data Models

### User Model
```python
{
  "id": 1,
  "username": "demo_farmer",
  "email": "demo@farm.local",
  "password_hash": "pbkdf2:sha256:...",
  "created_at": "2024-02-22T10:00:00",
  "updated_at": "2024-02-22T10:00:00"
}
```

### PredictionHistory Model
```python
{
  "id": 1,
  "user_id": 1,
  "prediction_type": "crop",
  "input_data": {
    "nitrogen": 40,
    "phosphorus": 30,
    "potassium": 40,
    "temperature": 25,
    "humidity": 60,
    "ph": 6.5,
    "rainfall": 1200
  },
  "prediction_result": "Wheat",
  "confidence": 0.87,
  "created_at": "2024-02-22T10:30:00"
}
```

---

## Client Examples

### Python Example
```python
import requests
import json

# Login
session = requests.Session()
login_data = {
    'username': 'demo_farmer',
    'password': 'demo_password_123'
}
session.post('http://localhost:5000/auth/login', data=login_data)

# Get crop recommendation
crop_data = {
    'nitrogen': 40,
    'phosphorus': 30,
    'potassium': 40,
    'temperature': 25,
    'humidity': 60,
    'ph': 6.5,
    'rainfall': 1200
}
response = session.post('http://localhost:5000/predict/crop', data=crop_data)
print(response.text)
```

### JavaScript Example
```javascript
// Login
async function login(username, password) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch('http://localhost:5000/auth/login', {
    method: 'POST',
    body: formData,
    credentials: 'include'
  });
  return response;
}

// Get crop recommendation
async function getCropRecommendation(data) {
  const formData = new FormData();
  Object.keys(data).forEach(key => {
    formData.append(key, data[key]);
  });
  
  const response = await fetch('http://localhost:5000/predict/crop', {
    method: 'POST',
    body: formData,
    credentials: 'include'
  });
  return response.text();
}

// Usage
await login('demo_farmer', 'demo_password_123');
await getCropRecommendation({
  nitrogen: 40,
  phosphorus: 30,
  // ... other parameters
});
```

---

## Webhooks (Future)

Planned for v2.0:
- Prediction completion notifications
- Daily recommendation summaries
- Weather-based alerts

---

## Versioning

Current API Version: 1.0
- Date: 2024-02-22
- Status: Stable
- Breaking changes will increment major version

---

## Support & Documentation

- **GitHub Issues**: Report bugs and request features
- **Email**: support@farmerconnect.local
- **Community Forum**: Coming soon

---

## License

This API is part of FarmersConnect and is licensed under the MIT License.
