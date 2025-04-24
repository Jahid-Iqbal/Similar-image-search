import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

# Load model with updated syntax
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model = torch.nn.Sequential(*(list(model.children())[:-1]))
model.eval()

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_features(img_path):
    try:
        img = Image.open(img_path).convert('RGB')
        img_tensor = preprocess(img)
        img_tensor = img_tensor.unsqueeze(0)
        with torch.no_grad():
            features = model(img_tensor)
        return features.flatten().numpy().tolist()
    except Exception as e:
        print(f"Error processing {img_path}: {str(e)}")
        return None