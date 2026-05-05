import sys
import os
import json
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import pickle

# Add current directory to path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.turtle_model import TurtleModel

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "no_input_path"}))
        sys.exit(1)
        
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(json.dumps({"error": "file_not_found", "path": image_path}))
        sys.exit(1)

    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "models", "best_384.pth")
        embeddings_path = os.path.join(base_dir, "models", "embeddings.pkl")
        train_dir = os.path.join(os.path.dirname(base_dir), "datasets", "train")
        
        # 1. Determine number of classes from dataset
        if os.path.exists(train_dir):
            classes = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])
            num_classes = len(classes)
        else:
            num_classes = 367 # User specified value as fallback
            classes = [f"t{i:03d}" for i in range(1, 368)]

        # 2. Load Model
        model = TurtleModel(num_classes=num_classes, pretrained=False).to(device)
        
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=device)
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["model_state_dict"])
            else:
                model.load_state_dict(checkpoint)
        model.eval()

        # 3. Load Embeddings Gallery
        if os.path.exists(embeddings_path):
            with open(embeddings_path, "rb") as f:
                gallery = pickle.load(f)
        else:
            # Fallback if no embeddings pkl (should ideally be generated)
            gallery = {}

        # 4. Prepare Image
        transform = transforms.Compose([
            transforms.Resize((384, 384)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        img = Image.open(image_path).convert('RGB')
        img_tensor = transform(img).unsqueeze(0).to(device)

        # 5. Inference
        with torch.no_grad():
            query_emb = model(img_tensor)
            query_emb = F.normalize(query_emb, dim=1).cpu().numpy().flatten()

        # 6. Match with Gallery
        best_id = "unknown"
        max_sim = 0.0
        
        if gallery:
            for turtle_id, ref_emb in gallery.items():
                sim = np.dot(query_emb, ref_emb.flatten()) / (np.linalg.norm(query_emb) * np.linalg.norm(ref_emb.flatten()) + 1e-8)
                if sim > max_sim:
                    max_sim = sim
                    best_id = turtle_id
        else:
            # If no gallery, we can't do individual ID, maybe return top class from classifier head?
            # But the user wants ID. 
            best_id = "gallery_not_found"

        result = {
            "pred": best_id,
            "conf": float(max_sim),
            "info": f"Processed with best_384.pth on {device}"
        }
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": "processing_error", "msg": str(e)}))
        sys.exit(2)

if __name__ == '__main__':
    main()
