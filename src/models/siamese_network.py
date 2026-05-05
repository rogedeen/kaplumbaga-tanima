import torch
import torch.nn as nn
from torchvision import models

class SiameseResNet50(nn.Module):
    def __init__(self, embedding_dim=256):
        super(SiameseResNet50, self).__init__()
        # 1. Load Pretrained ResNet50
        self.resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        
        # 2. Freeze all layers initially
        for param in self.resnet.parameters():
            param.requires_grad = False
            
        # 3. Unfreeze only Layer 4 and FC layer for training
        # ResNet50 structure: conv1, bn1, relu, maxpool, layer1, layer2, layer3, layer4
        for param in self.resnet.layer4.parameters():
            param.requires_grad = True
            
        # 4. Modify FC layer to produce embeddings and ensure it's trainable
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim)
        )
        for param in self.resnet.fc.parameters():
            param.requires_grad = True

    def forward_one(self, x):
        return self.resnet(x)

    def forward(self, anchor, positive, negative):
        embedded_a = self.forward_one(anchor)
        embedded_p = self.forward_one(positive)
        embedded_n = self.forward_one(negative)
        return embedded_a, embedded_p, embedded_n
