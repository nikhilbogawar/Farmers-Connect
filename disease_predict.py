import torch
from PIL import Image
import torchvision.transforms as transforms

# Load model
model = torch.load("models/plant_disease_model.pt", map_location="cpu")
model.eval()

# Define transform (must match training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def predict_disease(image_path):
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)

    return predicted.item()