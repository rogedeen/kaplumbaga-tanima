import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import os
import pickle
import logging
from tqdm import tqdm
from datetime import datetime
from PIL import Image

from src.models.turtle_model import TurtleModel
from src.models.arcface import ArcFace
from src.data.dataloader import get_dataloaders

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/training.log",
    level=logging.INFO,
    format="[%(asctime)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def save_embeddings(model, train_loader, device, output_path):
    model.eval()
    embeddings_dict = {}
    
    # We map identity (folder name) to its embedding
    dataset = train_loader.dataset
    class_to_idx = dataset.class_to_idx
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    
    temp_embeddings = {i: [] for i in range(len(dataset.classes))}
    
    with torch.no_grad():
        for i in range(min(len(dataset), 5000)): # Limit to 5000 samples for speed or use all
            path, label = dataset.samples[i]
            img = dataset.transform(Image.open(path).convert('RGB')).unsqueeze(0).to(device)
            emb = model(img)
            temp_embeddings[label].append(emb)
            
        for label, embs in temp_embeddings.items():
            if embs:
                mean_emb = torch.mean(torch.cat(embs, dim=0), dim=0)
                embeddings_dict[idx_to_class[label]] = mean_emb.cpu().numpy()
            
    with open(output_path, "wb") as f:
        pickle.dump(embeddings_dict, f)
    logging.info(f"Embeddings saved to {output_path}")

def train():
    # Hyperparameters
    BATCH_SIZE = 32
    EPOCHS = 100
    LR = 0.001
    LR_BACKBONE = 0.0001
    EMBEDDING_DIM = 512
    # ArcFace params
    S = 30.0
    M = 0.50
    LABEL_SMOOTHING = 0.1
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    TRAIN_DIR = "datasets/train"
    RUN_NAME = f"ArcFace_ConvNeXt_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Init Data and Model
    train_loader = get_dataloaders(TRAIN_DIR, batch_size=BATCH_SIZE)
    num_classes = len(train_loader.dataset.classes)
    
    model = TurtleModel(num_classes=num_classes, embedding_dim=EMBEDDING_DIM).to(DEVICE)
    metric_fc = ArcFace(EMBEDDING_DIM, num_classes, s=S, m=M, ls_eps=LABEL_SMOOTHING).to(DEVICE)

    # Optimizer
    optimizer = optim.AdamW([
        {'params': model.backbone.parameters(), 'lr': LR_BACKBONE},
        {'params': model.fc.parameters(), 'lr': LR},
        {'params': metric_fc.parameters(), 'lr': LR}
    ], weight_decay=5e-4)
    
    criterion = nn.CrossEntropyLoss()
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
    
    writer = SummaryWriter(f"logs/runs/{RUN_NAME}")
    
    best_acc = 0.0
    early_stop_patience = 15
    patience_counter = 0

    logging.info(f"Starting ArcFace training on {DEVICE} for {EPOCHS} epochs.")
    logging.info(f"Classes: {num_classes}, Backbone: ConvNeXt-Tiny")

    for epoch in range(EPOCHS):
        model.train()
        metric_fc.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        loop = tqdm(train_loader, total=len(train_loader), leave=False)
        for batch_idx, (images, labels) in enumerate(loop):
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            
            optimizer.zero_grad()
            embeddings = model(images)
            outputs = metric_fc(embeddings, labels)
            
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            loop.set_description(f"Epoch [{epoch+1}/{EPOCHS}]")
            loop.set_postfix(loss=loss.item(), acc=100.*correct/total)

        scheduler.step()
        epoch_loss = running_loss / len(train_loader)
        epoch_acc = 100. * correct / total
        
        writer.add_scalar("Loss/train", epoch_loss, epoch)
        writer.add_scalar("Accuracy/train", epoch_acc, epoch)
        
        msg = f"Epoch {epoch+1}/{EPOCHS} complete. Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.2f}%"
        print(msg)
        logging.info(msg)

        # Save Best Model based on Accuracy
        if epoch_acc > best_acc:
            best_acc = epoch_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'metric_fc_state_dict': metric_fc.state_dict(),
                'epoch': epoch,
                'acc': best_acc,
            }, "src/models/turtle_arcface_best.pth")
            
            # Legacy compatibility
            torch.save(model.state_dict(), "src/models/turtle_siamese_best.pth")
            
            logging.info(f"New best model saved with accuracy {best_acc:.2f}%")
            patience_counter = 0
            
            # Update embeddings for inference
            save_embeddings(model, train_loader, DEVICE, "src/models/embeddings.pkl")
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                logging.info("Early stopping triggered.")
                break

    writer.close()
    logging.info("Training finished.")

if __name__ == "__main__":
    train()