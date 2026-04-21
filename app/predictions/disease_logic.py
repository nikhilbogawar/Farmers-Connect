import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

CLASSES = [
    'Potato_Early_blight',
    'Potato_healthy',
    'Potato_Late_blight',
    'Tomato_Bacterial_spot',
    'Tomato_Early_blight',
    'Tomato_Late_blight'
]

def predict_disease(image_path):
    model = models.mobilenet_v2(pretrained=False)
    model.classifier[1] = nn.Linear(model.last_channel, len(CLASSES))

    model_path = os.path.join('models', 'plant_disease_model.pt')
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return CLASSES[predicted.item()]