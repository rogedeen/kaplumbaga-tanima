import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from src.data.dataloader import get_dataloaders
from src.models.siamese_network import SiameseResNet50
import os

def train():
    # 1. Hyperparameters
    batch_size = 32
    epochs = 20
    learning_rate = 1e-4
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 2. Paths
    base_path = os.getcwd()
    train_dir = os.path.join(base_path, 'datasets', 'train')
    
    # 3. DataLoader
    train_loader = get_dataloaders(train_dir, batch_size=batch_size)

    # 4. Model, Loss, Optimizer
    model = SiameseResNet50(embedding_dim=256).to(device)
    criterion = nn.TripletMarginLoss(margin=1.0, p=2)
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)

    # 5. Training Loop
    model.train()
    best_loss = float('inf')

    for epoch in range(epochs):
        running_loss = 0.0
        for i, (anchor, positive, negative) in enumerate(train_loader):
            anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

            optimizer.zero_grad()
            emb_a, emb_p, emb_n = model(anchor, positive, negative)
            
            loss = criterion(emb_a, emb_p, emb_n)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            
            if i % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}], Step [{i}/{len(train_loader)}], Loss: {loss.item():.4f}")

        avg_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{epochs}] Average Loss: {avg_loss:.4f}")

        # Save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), 'turtle_siamese_best.pth')
            print("Model saved as turtle_siamese_best.pth")

    print("Training finished.")

if __name__ == "__main__":
    train()
