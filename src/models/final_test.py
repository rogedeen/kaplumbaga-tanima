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

# Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "src", "models", "turtle_siamese_best.pth")
TEST_DATA_DIR = os.path.join(BASE_DIR, "datasets", "test")
EMBEDDINGS_CACHE = os.path.join(BASE_DIR, "src", "models", "embeddings.pkl")
REPORT_FILE = os.path.join(BASE_DIR, "logs", "test_accuracy_report.md")
REVIEWER_LOG_FILE = os.path.join(BASE_DIR, "logs", "agent_reviewer_log.md")

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

def log_reviewer_action(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(REVIEWER_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] - REVIEWER: {action}\n")

def run_final_test():
    log_reviewer_action("Nihai test süreci başlatıldı.")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load model
    model = SiameseResNet50()
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        log_reviewer_action(f"Model yüklendi: {MODEL_PATH}")
    else:
        print(f"Error: Model not found at {MODEL_PATH}")
        return

    model.to(device)
    model.eval()

    # Load reference embeddings
    if not os.path.exists(EMBEDDINGS_CACHE):
        print(f"Error: Embeddings cache not found at {EMBEDDINGS_CACHE}")
        return
    
    with open(EMBEDDINGS_CACHE, 'rb') as f:
        ref_embeddings = pickle.load(f)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    results = []
    correct_count = 0
    total_count = 0

    # Iterate through test folders
    test_folders = [f for f in os.listdir(TEST_DATA_DIR) if os.path.isdir(os.path.join(TEST_DATA_DIR, f))]
    test_folders.sort()

    for turtle_id in test_folders:
        folder_path = os.path.join(TEST_DATA_DIR, turtle_id)
        images = [img for img in os.listdir(folder_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for img_name in images:
            img_path = os.path.join(folder_path, img_name)
            try:
                img = Image.open(img_path).convert('RGB')
                img_tensor = transform(img).unsqueeze(0).to(device)
                
                with torch.no_grad():
                    query_emb = model(img_tensor).cpu().numpy().flatten()
                
                best_id = None
                max_sim = -1.0
                
                for ref_id, ref_emb in ref_embeddings.items():
                    sim = np.dot(query_emb, ref_emb.flatten()) / (np.linalg.norm(query_emb) * np.linalg.norm(ref_emb.flatten()) + 1e-8)
                    if sim > max_sim:
                        max_sim = sim
                        best_id = ref_id
                
                is_correct = (best_id == turtle_id)
                if is_correct:
                    correct_count += 1
                total_count += 1
                
                status = "Doğru" if is_correct else f"Yanlış (Tahmin: {best_id})"
                results.append(f"{turtle_id}: %{max_sim*100:.1f} güven - {status}")
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")

    # Write Report
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Nihai Test Doğruluk Raporu\n\n")
        f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Toplam Görsel:** {total_count}\n")
        f.write(f"**Doğru Tahmin:** {correct_count}\n")
        f.write(f"**Genel Doğruluk Oranı:** %{accuracy:.2f}\n\n")
        f.write("## Detaylı Sonuçlar\n\n")
        for res in results:
            f.write(f"- {res}\n")

    log_reviewer_action(f"Test tamamlandı. Doğruluk: %{accuracy:.2f}. Rapor oluşturuldu.")
    print(f"DONE: Accuracy %{accuracy:.2f}")

if __name__ == "__main__":
    run_final_test()
