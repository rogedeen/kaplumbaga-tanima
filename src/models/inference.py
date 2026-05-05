import os
import sys
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2
import pickle
import logging
from datetime import datetime

# Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AGENT_LOG_FILE = os.path.join(BASE_DIR, "logs", "agent_inference_log.md")
OUTPUT_HEATMAP_DIR = os.path.join(BASE_DIR, "output", "heatmaps")
MODEL_PATH = os.path.join(BASE_DIR, "src", "models", "best_model.pth")
TRAIN_DATA_DIR = os.path.join(BASE_DIR, "datasets", "train")
EMBEDDINGS_CACHE = os.path.join(BASE_DIR, "src", "models", "embeddings.pkl")

# Manual Logging Helper (Anayasaya uygun)
def log_agent_action(action, error=None, next_step=None):
    os.makedirs(os.path.dirname(AGENT_LOG_FILE), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {action}"
    if error:
        log_entry += f" - HATA: {error}"
    if next_step:
        log_entry += f" - {next_step}"
    
    with open(AGENT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

# Siamese Network Model (Matching the definition in siamese_network.py)
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

class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.hook_layers()

    def hook_layers(self):
        def forward_hook(module, input, output):
            self.activations = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_heatmap(self, input_image, target_index=None):
        self.model.zero_grad()
        output = self.model(input_image)
        
        if target_index is None:
            target_index = output.argmax(dim=1).item()
        
        # In a Siamese embedding context, we might want to visualize what triggered the embedding
        # We'll use the norm or a specific dimension if needed, but here we use the sum of embeddings as a proxy
        score = output[:, target_index] if len(output.shape) > 1 else output.sum()
        score.backward()

        gradients = self.gradients.cpu().data.numpy()[0]
        activations = self.activations.cpu().data.numpy()[0]

        weights = np.mean(gradients, axis=(1, 2))
        heatmap = np.zeros(activations.shape[1:], dtype=np.float32)

        for i, w in enumerate(weights):
            heatmap += w * activations[i]

        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap) if np.max(heatmap) != 0 else 1
        return heatmap

def save_gradcam(heatmap, original_image_path, output_path):
    # Use PIL to avoid path issues with OpenCV on Windows
    try:
        img_pil = Image.open(original_image_path).convert('RGB')
        img = np.array(img_pil)
        
        heatmap_resize = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap_uint8 = np.uint8(255 * heatmap_resize)
        heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        heatmap_color_rgb = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

        # Superimpose
        composite = (heatmap_color_rgb * 0.4 + img * 0.6).astype(np.uint8)
        
        # Save using PIL to ensure path handling
        result_img = Image.fromarray(composite)
        result_img.save(output_path)
        log_agent_action(f"Heatmap kaydedildi: {output_path}")
    except Exception as e:
        log_agent_action(f"Heatmap kaydedilirken hata oluştu: {output_path}", error=str(e), next_step="Dosya izinlerini ve disk alanını kontrol et.")
        print(json.dumps({"error": f"Grad-CAM save failed: {str(e)}"}))

def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SiameseResNet50().to(device)
    if os.path.exists(MODEL_PATH):
        try:
            model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
            log_agent_action(f"Model yüklendi: {MODEL_PATH}")
        except Exception as e:
            log_agent_action(f"Model yüklenirken hata oluştu: {MODEL_PATH}", error=str(e), next_step="Model binary dosyasının bozuk olup olmadığını kontrol et.")
    else:
        log_agent_action("Model dosyası bulunamadı. Testler için rastgele ağırlıklarla devam ediliyor.", next_step="Eğitim sürecini kontrol et veya best_model.pth dosyasını src/models altına koy.")
    model.eval()
    return model, device

def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def generate_embeddings_cache(model, device):
    log_agent_action("Referans embedding önbelleği oluşturuluyor...")
    transform = get_transforms()
    reference_embeddings = {}
    
    if not os.path.exists(TRAIN_DATA_DIR):
        log_agent_action(f"Eğitim dizini bulunamadı: {TRAIN_DATA_DIR}", error="DirectoryNotFound", next_step="Dataset dizin yapısını kontrol et.")
        return {}

    for turtle_id in os.listdir(TRAIN_DATA_DIR):
        turtle_path = os.path.join(TRAIN_DATA_DIR, turtle_id)
        if os.path.isdir(turtle_path):
            embeddings = []
            for img_name in os.listdir(turtle_path):
                if img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(turtle_path, img_name)
                    try:
                        img = Image.open(img_path).convert('RGB')
                        img_tensor = transform(img).unsqueeze(0).to(device)
                        with torch.no_grad():
                            emb = model(img_tensor)
                        embeddings.append(emb.cpu().numpy())
                    except Exception as e:
                        log_agent_action(f"Görüntü işlenirken hata: {img_path}", error=str(e))
            
            if embeddings:
                # Average embedding for the turtle
                reference_embeddings[turtle_id] = np.mean(np.vstack(embeddings), axis=0)
    
    with open(EMBEDDINGS_CACHE, 'wb') as f:
        pickle.dump(reference_embeddings, f)
    log_agent_action(f"Embedding önbelleği kaydedildi: {EMBEDDINGS_CACHE}")
    return reference_embeddings

def get_reference_embeddings(model, device):
    if os.path.exists(EMBEDDINGS_CACHE):
        try:
            with open(EMBEDDINGS_CACHE, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            log_agent_action("Embedding önbelleği yüklenirken hata oluştu", error=str(e), next_step="Önbelleği yeniden oluşturmak için dosyayı sil.")
    
    return generate_embeddings_cache(model, device)

def run_inference(image_path):
    log_agent_action(f"Inference başlatılıyor: {image_path}")
    
    if not os.path.exists(image_path):
        error_msg = f"Dosya bulunamadı: {image_path}"
        log_agent_action(f"Inference başarısız: {image_path}", error=error_msg, next_step="Dosya yolunun doğruluğunu kontrol et.")
        result = {"error": error_msg}
        print(json.dumps(result))
        return

    model, device = load_model()
    ref_embeddings = get_reference_embeddings(model, device)
    
    if not ref_embeddings:
        error_msg = "Referans embedding'ler mevcut değil."
        log_agent_action("Inference durduruldu", error=error_msg, next_step="datasets/train dizinini ve içeriğini kontrol et.")
        result = {"error": error_msg}
        print(json.dumps(result))
        return

    # Image Preprocessing
    transform = get_transforms()
    img = Image.open(image_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0).to(device)
    img_tensor.requires_grad = True

    # Get Embedding for Input
    embedding = model(img_tensor)
    query_emb = embedding.detach().cpu().numpy().flatten()

    # Calculate Similarities
    best_id = None
    max_sim = -1.0
    
    for turtle_id, ref_emb in ref_embeddings.items():
        # Cosine Similarity
        sim = np.dot(query_emb, ref_emb.flatten()) / (np.linalg.norm(query_emb) * np.linalg.norm(ref_emb.flatten()) + 1e-8)
        if sim > max_sim:
            max_sim = sim
            best_id = turtle_id

    # Generate Grad-CAM
    # Target layer is resnet.layer4 (last convolutional block)
    cam = GradCAM(model, model.resnet.layer4)
    heatmap = cam.generate_heatmap(img_tensor)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    heatmap_filename = f"heat_{timestamp}.jpg"
    heatmap_path = os.path.join(OUTPUT_HEATMAP_DIR, heatmap_filename)
    
    os.makedirs(OUTPUT_HEATMAP_DIR, exist_ok=True)
    save_gradcam(heatmap, image_path, heatmap_path)

    # Prepare Output
    result = {
        "turtle_id": best_id,
        "confidence": float(max_sim),
        "heatmap_path": os.path.relpath(heatmap_path, BASE_DIR)
    }
    
    print(json.dumps(result))
    log_agent_action(f"Inference tamamlandı. ID: {best_id}, Confidence: {max_sim:.4f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided."}))
    else:
        run_inference(sys.argv[1])
