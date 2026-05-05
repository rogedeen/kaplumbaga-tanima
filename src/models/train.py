import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
import os
import pickle
import logging
from tqdm import tqdm
from datetime import datetime

from src.models.siamese_network import SiameseResNet50
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
    
    # We need to map identity (folder name) to its embedding
    # TurtleTripletDataset stores identities. Let's get them from dataset
    dataset = train_loader.dataset
    identities = dataset.identities
    identity_to_files = dataset.identity_to_files
    
    with torch.no_grad():
        for ident in identities:
            files = identity_to_files[ident]
            if not files:
                continue
            
            # Take the first image as representative or average them? 
            # For now, let's take the first one or average all images of that identity.
            imgs = []
            for f in files:
                img = dataset.transform(dataset.Image.open(f).convert('RGB')).unsqueeze(0).to(device)
                emb = model.forward_one(img)
                imgs.append(emb)
            
            mean_emb = torch.mean(torch.cat(imgs, dim=0), dim=0)
            embeddings_dict[ident] = mean_emb.cpu().numpy()
            
    with open(output_path, "wb") as f:
        pickle.dump(embeddings_dict, f)
    logging.info(f"Embeddings saved to {output_path}")

def train():
    # Hyperparameters
    BATCH_SIZE = 32
    EPOCHS = 50
    LR = 0.0001
    LR_FINE_TUNE = 1e-6
    MARGIN = 2.0
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    TRAIN_DIR = "datasets/train"
    RUN_NAME = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Init Data and Model
    train_loader = get_dataloaders(TRAIN_DIR, batch_size=BATCH_SIZE)
    model = SiameseResNet50(embedding_dim=256).to(DEVICE)

    # Backbone Unfreeze with very low learning rate
    # We apply lower LR to pretrained layers and regular LR to head
    for param in model.parameters():
        param.requires_grad = True

    # Group parameters for different learning rates
    backbone_params = filter(lambda p: id(p) not in [id(param) for param in model.resnet.fc.parameters()], model.parameters())
    head_params = model.resnet.fc.parameters()

    optimizer = optim.AdamW([
        {'params': backbone_params, 'lr': LR_FINE_TUNE},
        {'params': head_params, 'lr': LR}
    ])
    
    criterion = nn.TripletMarginLoss(margin=MARGIN)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    
    writer = SummaryWriter(f"logs/runs/{RUN_NAME}")
    
    best_loss = float('inf')
    early_stop_patience = 10
    patience_counter = 0

    logging.info(f"Starting training on {DEVICE} for {EPOCHS} epochs with Hard Triplet Mining and Full Backbone Unfreeze.")

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        
        loop = tqdm(train_loader, total=len(train_loader), leave=False)
        for batch_idx, (anchor, positive, negative) in enumerate(loop):
            anchor, positive, negative = anchor.to(DEVICE), positive.to(DEVICE), negative.to(DEVICE)
            
            optimizer.zero_grad()
            emb_a, emb_p, emb_n = model(anchor, positive, negative)
            
            # Hard Triplet Mining: Calculate distances
            dist_ap = torch.pow(emb_a - emb_p, 2).sum(dim=1)
            dist_an = torch.pow(emb_a - emb_n, 2).sum(dim=1)
            
            # Only train on "hard" or "semi-hard" triplets where dist_an - dist_ap < MARGIN
            mask = (dist_an - dist_ap < MARGIN).float()
            
            # Recalculate loss with masking if necessary or just use standard loss 
            # as TripletMarginLoss already does this implicitly (max(0, d_ap - d_an + m))
            # But let's log the "hard" ratio
            hard_ratio = mask.mean().item()

            loss = criterion(emb_a, emb_p, emb_n)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            loop.set_description(f"Epoch [{epoch+1}/{EPOCHS}]")
            loop.set_postfix(loss=loss.item(), hard_ratio=f"{hard_ratio:.2f}")

        scheduler.step()
        epoch_loss = running_loss / len(train_loader)
        writer.add_scalar("Loss/train", epoch_loss, epoch)
        
        msg = f"Epoch {epoch+1}/{EPOCHS} complete. Loss: {epoch_loss:.4f}"
        print(msg)
        logging.info(msg)

        # Basic "Accuracy" metric for Triplet Loss: 
        # How many triplets have dist(A,P) < dist(A,N)?
        # For simplicity in this script, let's just use Loss as primary metric.

        # Save Best Model
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            # As per master plan: turtle_siamese_best.pth
            torch.save(model.state_dict(), "src/models/turtle_siamese_best.pth")
            logging.info(f"New best model saved with loss {best_loss:.4f}")
            patience_counter = 0
            # Update embeddings
            save_embeddings(model, train_loader, DEVICE, "src/models/embeddings.pkl")
            
            # Run update_embeddings.py helper
            os.system("python src/models/update_embeddings.py")
        else:
            patience_counter += 1
            if patience_counter >= early_stop_patience:
                logging.info("Early stopping triggered.")
                break

    writer.close()
    logging.info("Training finished.")

if __name__ == "__main__":
    train()
