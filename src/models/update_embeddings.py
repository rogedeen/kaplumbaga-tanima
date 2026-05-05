import torch
import os
import pickle
import sys
from PIL import Image

# Proje kök dizinini path'e ekle
sys.path.append(os.getcwd())

from src.models.siamese_network import SiameseResNet50
from src.data.dataloader import get_dataloaders
from torchvision import transforms

def update_embeddings():
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    MODEL_PATH = "src/models/turtle_siamese_best.pth"
    EMBEDDINGS_PATH = "src/models/embeddings.pkl"
    TRAIN_DIR = "datasets/train"
    
    print(f"Loading model from {MODEL_PATH}...")
    model = SiameseResNet50(embedding_dim=256).to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    
    print("Preparing dataloader...")
    # Dataset nesnesine erişmek için loader alıyoruz
    train_loader = get_dataloaders(TRAIN_DIR, batch_size=1)
    dataset = train_loader.dataset
    identities = dataset.identities
    identity_to_files = dataset.identity_to_files
    
    embeddings_dict = {}
    
    print(f"Generating embeddings for {len(identities)} identities...")
    with torch.no_grad():
        for ident in identities:
            files = identity_to_files[ident]
            if not files:
                continue
            
            imgs_embs = []
            for f in files:
                img = dataset.transform(Image.open(f).convert('RGB')).unsqueeze(0).to(DEVICE)
                emb = model.forward_one(img)
                imgs_embs.append(emb)
            
            # Ortalama embedding'i hesapla
            mean_emb = torch.mean(torch.cat(imgs_embs, dim=0), dim=0)
            embeddings_dict[ident] = mean_emb.cpu().numpy()
            
    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(embeddings_dict, f)
    
    print(f"Successfully saved updated embeddings to {EMBEDDINGS_PATH}")

if __name__ == "__main__":
    update_embeddings()
