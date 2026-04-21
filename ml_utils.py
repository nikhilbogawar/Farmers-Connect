"""
Machine Learning Utilities for FarmersConnect
Handles loading pre-trained models and making predictions
"""

import os
import pickle
import logging
import numpy as np
from pathlib import Path
from PIL import Image
from config import Config

# Optional PyTorch import - will be loaded lazily if needed
torch = None
torchvision = None

# Setup logging
logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
_model_cache = {}

# Comprehensive crop information database
CROP_INFO = {
    'rice': {
        'name': 'Rice',
        'description': 'Staple cereal grain, rich in carbohydrates',
        'optimal_temp': '25-35°C',
        'water': 'High water requirement (1000-1500mm)',
        'soil': 'Loamy or clayey soil with good drainage',
        'season': 'Monsoon season',
        'benefits': 'High nutritional value, good crop yield',
        'npk_ratio': '18:46:0 base + maintenance doses'
    },
    'wheat': {
        'name': 'Wheat',
        'description': 'Major staple crop, protein-rich grain',
        'optimal_temp': '15-25°C',
        'water': 'Moderate water requirement (450-650mm)',
        'soil': 'Well-drained loamy soil',
        'season': 'Winter season',
        'benefits': 'Rich in protein and fiber, excellent yield',
        'npk_ratio': '120:60:40 per hectare'
    },
    'corn': {
        'name': 'Corn/Maize',
        'description': 'Versatile crop for food and feed',
        'optimal_temp': '21-27°C',
        'water': 'Moderate-high water requirement (400-500mm)',
        'soil': 'Rich loamy soil with organic matter',
        'season': 'Kharif/Summer',
        'benefits': 'High yield, multiple uses',
        'npk_ratio': '150:75:40 per hectare'
    },
    'potato': {
        'name': 'Potato',
        'description': 'Tuber crop, important staple food',
        'optimal_temp': '18-24°C',
        'water': 'High water requirement during tuber formation',
        'soil': 'Well-drained loamy soil',
        'season': 'Winter and summer',
        'benefits': 'High nutritional value, good storage',
        'npk_ratio': '80:100:60 per hectare'
    },
    'sugarcane': {
        'name': 'Sugarcane',
        'description': 'Cash crop for sugar and biofuel production',
        'optimal_temp': '20-30°C',
        'water': 'High water requirement (1500-2250mm)',
        'soil': 'Deep fertile loamy soil',
        'season': 'Year-round crop',
        'benefits': 'High income, industrial use',
        'npk_ratio': '150:75:75 per hectare'
    }
}

# Fertilizer information database
FERTILIZER_INFO = {
    'npk_10_10_10': {
        'name': 'NPK 10:10:10 (Balanced)',
        'nitrogen': 10,
        'phosphorus': 10,
        'potassium': 10,
        'description': 'Balanced fertilizer for general maintenance',
        'best_for': 'Vegetables, fruits, and maintenance feeding',
        'application': '1 kg per 30-40 sq.m',
        'features': 'Promotes overall plant growth, good for most crops'
    },
    'npk_15_15_15': {
        'name': 'NPK 15:15:15 (Premium Balanced)',
        'nitrogen': 15,
        'phosphorus': 15,
        'potassium': 15,
        'description': 'Premium balanced complete fertilizer',
        'best_for': 'Intensive crops, vegetables, fruits',
        'application': '750g per 30-40 sq.m',
        'features': 'Higher nutrient concentration, better results'
    },
    'npk_20_10_10': {
        'name': 'NPK 20:10:10 (High Nitrogen)',
        'nitrogen': 20,
        'phosphorus': 10,
        'potassium': 10,
        'description': 'High nitrogen formula for leafy growth',
        'best_for': 'Leafy vegetables, grasses, foliage crops',
        'application': '600g per 30-40 sq.m',
        'features': 'Promotes vegetative growth and green color'
    },
    'npk_10_52_10': {
        'name': 'NPK 10:52:10 (DAP)',
        'nitrogen': 10,
        'phosphorus': 52,
        'potassium': 10,
        'description': 'Phosphorus-rich for root and flower development',
        'best_for': 'Root crops, flowering plants, seedlings',
        'application': '500g per 30-40 sq.m',
        'features': 'Excellent for flowering and fruiting'
    }
}

# Disease information database
DISEASE_INFO = {
    'Early Blight': {
        'name': 'Early Blight',
        'symptoms': 'Brown lesions with concentric rings on older leaves, yellowing around spots',
        'cause': 'Fungal disease - Alternaria solani',
        'severity': 'Moderate',
        'treatment': [
            'Remove infected leaves immediately',
            'Use copper or mancozeb fungicide (every 7-10 days)',
            'Ensure proper spacing for air circulation',
            'Destroy crop debris after harvest',
            'Use disease-resistant varieties'
        ],
        'prevention': [
            'Rotate crops yearly',
            'Use certified seed',
            'Avoid overhead watering',
            'Maintain field hygiene',
            'Monitor plants regularly'
        ]
    },
    'Late Blight': {
        'name': 'Late Blight',
        'symptoms': 'Water-soaked spots on leaves and stems, white fungal growth on leaf undersides',
        'cause': 'Fungal disease - Phytophthora infestans',
        'severity': 'High - can destroy entire crop',
        'treatment': [
            'Apply systemic fungicide (Metalaxyl or Flumorph)',
            'Increase ventilation around plants',
            'Remove affected parts immediately',
            'Apply fungicide every 5-7 days during wet season',
            'Use resistant varieties if available'
        ],
        'prevention': [
            'Use certified disease-free seed',
            'Maintain adequate spacing',
            'Avoid overhead irrigation',
            'Rotate crops',
            'Remove volunteer plants'
        ]
    },
    'Healthy': {
        'name': 'Healthy Plant',
        'symptoms': 'No visible disease symptoms',
        'cause': 'Plant is disease-free',
        'severity': 'None',
        'treatment': [
            'Continue regular care and maintenance',
            'Monitor for any changes in appearance',
            'Maintain proper watering schedule',
            'Apply preventive doses of fungicide during wet season',
            'Ensure good drainage'
        ],
        'prevention': [
            'Continue crop rotation',
            'Regular field monitoring',
            'Proper nutrient management',
            'Adequate spacing between plants',
            'Timely harvesting'
        ]
    },
    'Powdery Mildew': {
        'name': 'Powdery Mildew',
        'symptoms': 'White powder-like coating on leaves, stems, and flowers',
        'cause': 'Fungal disease - Oidium or Erysiphe species',
        'severity': 'Moderate',
        'treatment': [
            'Apply sulfur powder or spray (every 7-10 days)',
            'Use neem oil or potassium bicarbonate',
            'Increase air circulation',
            'Remove heavily infected leaves',
            'Reduce humidity levels'
        ],
        'prevention': [
            'Maintain good air circulation',
            'Avoid excess nitrogen fertilizer',
            'Water at base of plants',
            'Remove infected plant material',
            'Use resistant varieties'
        ]
    },
    'Leaf Spot': {
        'name': 'Leaf Spot',
        'symptoms': 'Circular brown or black spots with yellow halo on leaves',
        'cause': 'Bacterial or fungal infection',
        'severity': 'Moderate',
        'treatment': [
            'Remove infected leaves completely',
            'Apply copper-based fungicide',
            'Improve ventilation',
            'Reduce leaf wetness by proper irrigation',
            'Space plants adequately'
        ],
        'prevention': [
            'Avoid overhead spraying',
            'Water in early morning',
            'Maintain crop hygiene',
            'Rotate crops',
            'Use disease-free seeds'
        ]
    }
}


def load_crop_model():
    """Load pre-trained Crop Recommendation Model"""
    try:
        model_path = os.path.join(Config.MODELS_FOLDER, 'crop_model.pkl')
        
        # Return cached model if available
        if 'crop_model' in _model_cache:
            return _model_cache['crop_model']
        
        # Check if model exists
        if not os.path.exists(model_path):
            logger.warning(f"Crop model not found at {model_path}. Creating placeholder.")
            # Return a placeholder that predicts rice
            return PlaceholderModel('wheat')
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            _model_cache['crop_model'] = model
            logger.info("Crop model loaded successfully")
            return model
    except Exception as e:
        logger.error(f"Error loading crop model: {str(e)}")
        return PlaceholderModel('rice')


def load_fertilizer_model():
    """Load pre-trained Fertilizer Recommendation Model"""
    try:
        model_path = os.path.join(Config.MODELS_FOLDER, 'fertilizer_model.pkl')
        
        if 'fertilizer_model' in _model_cache:
            return _model_cache['fertilizer_model']
        
        if not os.path.exists(model_path):
            logger.warning(f"Fertilizer model not found at {model_path}. Creating placeholder.")
            return PlaceholderModel('NPK 10-10-10')
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            _model_cache['fertilizer_model'] = model
            logger.info("Fertilizer model loaded successfully")
            return model
    except Exception as e:
        logger.error(f"Error loading fertilizer model: {str(e)}")
        return PlaceholderModel('NPK 15-15-15')


def load_disease_model():
    """Load pre-trained Disease Detection Model (PyTorch)"""
    try:
        # Lazy load PyTorch only if needed
        global torch, torchvision
        if torch is None or torchvision is None:
            try:
                import torch
                import torchvision
                import torchvision.transforms as transforms
            except ImportError:
                raise RuntimeError("PyTorch is required for disease prediction. Please install it using: pip install torch torchvision")

        model_path = os.path.join(Config.MODELS_FOLDER, 'plant_disease_model.pth')
        logger.info(f"Loading model from: {model_path}")
        logger.info(f"Model file exists: {os.path.exists(model_path)}")

        # Check cache first
        if 'disease_model' in _model_cache:
            logger.debug("Using cached disease model")
            return _model_cache['disease_model']

        # If model not present but a labeled dataset exists, attempt a quick transfer-learning train
        dataset_dir = os.path.join(Config.BASE_DIR, 'DATA_DIR')

        if not os.path.exists(model_path):
            # If user provided a dataset, try to train a model using transfer learning
            if os.path.isdir(dataset_dir) and any(os.scandir(dataset_dir)):
                logger.info("No disease_model.pth found — attempting to train a transfer-learning model from dataset.")
                try:
                    train_disease_model(dataset_dir, model_path, epochs=5, batch_size=16)
                    logger.info("Training completed and model saved.")
                except Exception as te:
                    logger.error(f"Training failed: {te}", exc_info=True)
                    raise RuntimeError(f"Failed to train disease model: {str(te)}")
            else:
                raise FileNotFoundError(f"Disease model not found at {model_path} and no training data available in {dataset_dir}")

        # Load PyTorch model
        try:
            # Load the model architecture
            model = build_disease_model(num_classes=5)  # Assuming 5 classes based on the disease info
            # Load the trained weights
            model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
            model.eval()  # Set to evaluation mode
            _model_cache['disease_model'] = model
            logger.info("Disease model loaded successfully")
            return model
        except Exception as load_e:
            logger.error(f"Failed to load PyTorch model: {load_e}", exc_info=True)
            raise RuntimeError(f"Failed to load disease model. The model file may be corrupted or incompatible. Error: {str(load_e)}")
    except Exception as e:
        logger.error(f"Error loading disease model: {str(e)}", exc_info=True)
        raise


def build_disease_model(num_classes):
    """Builds a MobileNetV2-based classifier for disease detection using PyTorch."""
    global torch, torchvision
    if torch is None or torchvision is None:
        try:
            import torch
            import torchvision
        except ImportError:
            raise RuntimeError("PyTorch is required to build disease model")

    # Load pre-trained MobileNetV2
    model = torchvision.models.mobilenet_v2(weights=torchvision.models.MobileNet_V2_Weights.IMAGENET1K_V1)
    model.classifier = torch.nn.Sequential(
        torch.nn.Dropout(0.3),
        torch.nn.Linear(model.last_channel, num_classes)
    )
    return model


def train_disease_model(dataset_dir, save_path, epochs=5, batch_size=16):
    """Train a disease detection model using transfer learning with PyTorch.

    Expects dataset_dir to have subfolders per class (standard ImageNet-style).
    Saves trained model to `save_path`.
    """
    # Import required modules
    import torch
    import torchvision
    import torchvision.transforms as transforms

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Training on device: {device}")

    # Data transforms
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Load dataset
    train_dataset = torchvision.datasets.ImageFolder(
        root=dataset_dir,
        transform=transform
    )

    # Create data loader
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0
    )

    num_classes = len(train_dataset.classes)
    logger.info(f"Found {num_classes} classes: {train_dataset.classes}")

    # Build model
    model = build_disease_model(num_classes)
    model = model.to(device)

    # Loss and optimizer
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    # Training loop
    model.train()
    total_batches = len(train_loader)
    for epoch in range(epochs):
        running_loss = 0.0
        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            # Print progress every 10 batches
            if (batch_idx + 1) % 10 == 0 or batch_idx == total_batches - 1:
                progress = (batch_idx + 1) / total_batches * 100
                print(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}/{total_batches} ({progress:.1f}%)")

        epoch_loss = running_loss / len(train_loader)
        logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}")

    # Save the model
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    logger.info(f"Model saved to {save_path}")
    return model


def predict_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    """
    Predict crop based on soil and environmental parameters
    
    Args:
        nitrogen (float): N level
        phosphorus (float): P level
        potassium (float): K level
        temperature (float): Temperature in Celsius
        humidity (float): Humidity percentage
        ph (float): Soil pH value
        rainfall (float): Rainfall in mm
    
    Returns:
        dict: Prediction result with detailed crop information
    """
    try:
        model = load_crop_model()
        
        # Prepare input data
        features = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
        
        # Make prediction
        if isinstance(model, PlaceholderModel):
            prediction = model.predict()
            confidence = 0.85
        else:
            prediction = model.predict(features)[0]
            probs = model.predict_proba(features)[0]
            confidence = float(max(probs))
            if confidence > 1:
                confidence = confidence / 100 
        
        # Normalize prediction to lowercase
        pred_lower = str(prediction).lower()
        
        # Get crop information
        crop_data = CROP_INFO.get(pred_lower, CROP_INFO.get('rice'))
        
        return {
            'crop': crop_data['name'],
            'confidence': round(confidence, 2),
            'description': crop_data['description'],
            'optimal_temperature': crop_data['optimal_temp'],
            'water_requirement': crop_data['water'],
            'soil_type': crop_data['soil'],
            'season': crop_data['season'],
            'benefits': crop_data['benefits'],
            'npk_requirement': crop_data['npk_ratio'],
            'success': True,
            'message': f"Recommended crop: {crop_data['name']} - {crop_data['description']}"
        }
    except Exception as e:
        logger.error(f"Error in crop prediction: {str(e)}")
        rice_data = CROP_INFO['rice']
        return {
            'crop': rice_data['name'],
            'confidence': 0.0,
            'description': rice_data['description'],
            'optimal_temperature': rice_data['optimal_temp'],
            'water_requirement': rice_data['water'],
            'soil_type': rice_data['soil'],
            'season': rice_data['season'],
            'benefits': rice_data['benefits'],
            'npk_requirement': rice_data['npk_ratio'],
            'success': False,
            'message': f'Error during prediction: {str(e)}'
        }


def predict_fertilizer(soil_type, crop_type, nitrogen, phosphorus, potassium):
    """
    Recommend fertilizer based on soil and crop parameters
    
    Args:
        soil_type (str): Type of soil
        crop_type (str): Type of crop
        nitrogen (float): Current N level
        phosphorus (float): Current P level
        potassium (float): Current K level
    
    Returns:
        dict: Fertilizer recommendation with detailed information
    """
    try:
        model = load_fertilizer_model()
        
        # Prepare input data (encode categorical variables)
        soil_encoding = {'loamy': 0, 'sandy': 1, 'clayey': 2}
        crop_encoding = {'rice': 0, 'wheat': 1, 'corn': 2, 'potato': 3, 'sugarcane': 4}
        
        soil_code = soil_encoding.get(soil_type.lower(), 0)
        crop_code = crop_encoding.get(crop_type.lower(), 0)
        
        features = np.array([[soil_code, crop_code, nitrogen, phosphorus, potassium]])
        
        # Determine fertilizer type based on nutrient levels
        if nitrogen < phosphorus and phosphorus > potassium:
            fert_type = 'npk_10_52_10'  # High phosphorus
        elif nitrogen > 15:
            fert_type = 'npk_20_10_10'  # High nitrogen
        elif nitrogen + phosphorus + potassium < 30:
            fert_type = 'npk_15_15_15'  # Premium balanced
        else:
            fert_type = 'npk_10_10_10'  # Standard balanced
        
        if isinstance(model, PlaceholderModel):
            fert_data = FERTILIZER_INFO.get(fert_type, FERTILIZER_INFO['npk_15_15_15'])
        else:
            # Use model prediction if available
            prediction = model.predict(features)[0]
            fert_type = prediction if prediction in FERTILIZER_INFO else fert_type
            fert_data = FERTILIZER_INFO.get(fert_type, FERTILIZER_INFO['npk_15_15_15'])
        
        return {
            'fertilizer': fert_data['name'],
            'nitrogen_content': fert_data['nitrogen'],
            'phosphorus_content': fert_data['phosphorus'],
            'potassium_content': fert_data['potassium'],
            'description': fert_data['description'],
            'best_for': fert_data['best_for'],
            'application_rate': fert_data['application'],
            'features': fert_data['features'],
            'soil_type': soil_type,
            'crop_type': crop_type,
            'current_npk': f"N:{nitrogen}, P:{phosphorus}, K:{potassium}",
            'success': True,
            'message': f"Recommended: {fert_data['name']} - {fert_data['description']}"
        }
    except Exception as e:
        logger.error(f"Error in fertilizer prediction: {str(e)}")
        fert_data = FERTILIZER_INFO['npk_15_15_15']
        return {
            'fertilizer': fert_data['name'],
            'nitrogen_content': fert_data['nitrogen'],
            'phosphorus_content': fert_data['phosphorus'],
            'potassium_content': fert_data['potassium'],
            'description': fert_data['description'],
            'best_for': fert_data['best_for'],
            'application_rate': fert_data['application'],
            'features': fert_data['features'],
            'soil_type': soil_type,
            'crop_type': crop_type,
            'current_npk': f"N:{nitrogen}, P:{phosphorus}, K:{potassium}",
            'success': False,
            'message': f'Error during prediction: {str(e)}'
        }


def predict_disease(image_path):
    """
    Predict plant disease from image using PyTorch CNN model

    Args:
        image_path (str): Path to plant leaf image

    Returns:
        dict: Disease prediction with detailed treatment recommendations
    """
    try:
        global torch, torchvision
        if torch is None or torchvision is None:
            import torch as torch_module
            import torchvision as torchvision_module
            import torchvision.transforms as transforms
            torch = torch_module
            torchvision = torchvision_module

        model = load_disease_model()

        # Define image transforms (same as training)
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension

        # Move to device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image_tensor = image_tensor.to(device)
        model = model.to(device)

        # Make prediction
        model.eval()
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            confidence = float(torch.max(probabilities).item()) * 100
            disease_idx = int(torch.argmax(probabilities).item())

        # Map indices to class names based on dataset directory order
        # These should match the order from training data
        class_names = [
            'Potato_Early_blight', 'Potato_healthy', 'Potato_Late_blight',
            'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight'
        ]

        # Handle cases where we have more/fewer classes than expected
        if disease_idx < len(class_names):
            disease_name = class_names[disease_idx]
        else:
            logger.warning(f"Disease index {disease_idx} out of range for class_names")
            disease_name = "Healthy"

        # Get detailed disease information
        disease_data = DISEASE_INFO.get(disease_name, DISEASE_INFO['Healthy'])

        logger.info(f"Disease prediction: {disease_name} (confidence: {confidence:.2f}%)")

        return str(disease_name)
    except Exception as e:
        logger.error(f"Error in disease prediction: {str(e)}", exc_info=True)
        healthy_data = DISEASE_INFO['Healthy']
        return "Error"


class PlaceholderModel:
    """Placeholder for scikit-learn models when files are not available"""
    
    def __init__(self, default_prediction='Rice'):
        self.default_prediction = default_prediction
    
    def predict(self, X=None):
        return self.default_prediction
    
    def predict_proba(self, X=None):
        # Return dummy probabilities
        return np.array([[0.85, 0.10, 0.05]])


def clear_model_cache():
    """Clear the model cache (useful for testing or memory management)"""
    global _model_cache
    _model_cache.clear()
    logger.info("Model cache cleared")
