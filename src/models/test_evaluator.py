import os
import sys
import json
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import pickle
from datetime import datetime
from tqdm import tqdm

# Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "src", "models", "turtle_siamese_best.pth")
TRAIN_DATA_DIR = os.path.join(BASE_DIR, "datasets", "train")
TEST_DATA_DIR = os.path.join(BASE_DIR, "datasets", "test")
EMBEDDINGS_CACHE = os.path.join(BASE_DIR, "src", "models", "embeddings.pkl")
REPORT_PATH = os.path.join(BASE_DIR, "logs", "test_accuracy_report.md")
REVIEWER_LOG_PATH = os.path.join(BASE_DIR, "logs", "agent_reviewer_log.md")

class SiameseResNet50(nn.Module):
    def __init__(self, embedding_dim=256):
        super(SiameseResNet50, self).__init__()
        self.resnet = models.resnet50(weights=None)
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, x):
        return self.resnet(x)

    def forward_one(self, x):
        return self.resnet(x)

def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SiameseResNet50().to(device)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()
    return model, device

def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def get_reference_embeddings(model, device):
    if os.path.exists(EMBEDDINGS_CACHE):
        with open(EMBEDDINGS_CACHE, 'rb') as f:
            return pickle.load(f)
    
    # Generate if not exists
    transform = get_transforms()
    reference_embeddings = {}
    for turtle_id in os.listdir(TRAIN_DATA_DIR):
        turtle_path = os.path.join(TRAIN_DATA_DIR, turtle_id)
        if os.path.isdir(turtle_path):
            embeddings = []
            for img_name in os.listdir(turtle_path):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(turtle_path, img_name)
                    img = Image.open(img_path).convert('RGB')
                    img_tensor = transform(img).unsqueeze(0).to(device)
                    with torch.no_grad():
                        emb = model(img_tensor)
                    embeddings.append(emb.cpu().numpy())
            if embeddings:
                reference_embeddings[turtle_id] = np.mean(np.vstack(embeddings), axis=0)
    
    with open(EMBEDDINGS_CACHE, 'wb') as f:
        pickle.dump(reference_embeddings, f)
    return reference_embeddings

def run_test_evaluation():
    model, device = load_model()
    ref_embeddings = get_reference_embeddings(model, device)
    transform = get_transforms()
    
    correct = 0
    total = 0
    results = []

    test_classes = [d for d in os.listdir(TEST_DATA_DIR) if os.path.isdir(os.path.join(TEST_DATA_DIR, d))]
    
    print(f"Evaluating {len(test_classes)} test classes...")
    
    for turtle_id in tqdm(test_classes):
        actual_id = turtle_id
        turtle_path = os.path.join(TEST_DATA_DIR, turtle_id)
        
        for img_name in os.listdir(turtle_path):
            if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(turtle_path, img_name)
                img = Image.open(img_path).convert('RGB')
                img_tensor = transform(img).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    embedding = model.forward_one(img_tensor)
                query_emb = embedding.cpu().numpy().flatten()
                
                best_id = None
                max_sim = -1.0
                
                for r_id, r_emb in ref_embeddings.items():
                    sim = np.dot(query_emb, r_emb.flatten()) / (np.linalg.norm(query_emb) * np.linalg.norm(r_emb.flatten()) + 1e-8)
                    if sim > max_sim:
                        max_sim = sim
                        best_id = r_id
                
                total += 1
                is_correct = (best_id == actual_id)
                if is_correct:
                    correct += 1
                
                results.append({
                    "image": img_name,
                    "actual": actual_id,
                    "predicted": best_id,
                    "confidence": float(max_sim),
                    "correct": is_correct
                })

    accuracy = (correct / total * 100) if total > 0 else 0
    
    # Create Report
    timestamp = datetime.now().strftime("%Y-%m-%d %X")
    report = f"""# Test Accuracy Report
Generated on: {timestamp}

## Overall Performance
- **Total Test Images:** {total}
- **Correct Predictions:** {correct}
- **Accuracy:** {accuracy:.2f}%

## Analysis
- Previous Accuracy: ~5% (Baseline)
- Current Accuracy: {accuracy:.2f}%
- Improvement: {accuracy - 5:.2f}%

## Success Criteria
- [ ] 30%+ Accuracy (Major Success)
- [ ] 10-20% Accuracy (Significant Improvement)

## Detailed Results (Samples)
| Image | Actual ID | Predicted ID | Confidence | Correct |
|-------|-----------|--------------|------------|---------|
"""
    for res in results[:20]: # First 20 results as sample
        report += f"| {res['image']} | {res['actual']} | {res['predicted']} | {res['confidence']:.4f} | {'✅' if res['correct'] else '❌'} |\n"
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
        
    # Update Reviewer Log
    log_entry = f"\n[{timestamp}] - TEST EVALUATION COMPLETED\n"
    log_entry += f"- Total Images: {total}\n"
    log_entry += f"- Accuracy: {accuracy:.2f}%\n"
    log_entry += f"- Result: {'SUCCESS (30%+ target met)' if accuracy >= 30 else 'IMPROVED but below 30%' if accuracy > 5 else 'NO IMPROVEMENT'}\n"
    
    with open(REVIEWER_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_entry)
        
    print(f"Evaluation complete. Accuracy: {accuracy:.2f}%")
    return accuracy

if __name__ == "__main__":
    run_test_evaluation()
