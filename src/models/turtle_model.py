import torch
import torch.nn as nn
import timm

class TurtleModel(nn.Module):
    def __init__(self, num_classes, model_name='convnext_tiny.fb_in22k_ft_in1k', embedding_dim=512, pretrained=True):
        super(TurtleModel, self).__init__()
        self.backbone = timm.create_model(model_name, pretrained=pretrained, num_classes=0, global_pool='avg')
        
        # Get backbone output features
        dummy_input = torch.randn(1, 3, 224, 224)
        with torch.no_grad():
            features = self.backbone(dummy_input)
            in_features = features.shape[1]
            
        self.bn1 = nn.BatchNorm1d(in_features)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(in_features, embedding_dim)
        self.bn2 = nn.BatchNorm1d(embedding_dim)
        
        # Initialization
        nn.init.constant_(self.bn1.weight, 1)
        nn.init.constant_(self.bn1.bias, 0)
        nn.init.kaiming_normal_(self.fc.weight, mode='fan_out', nonlinearity='relu')
        nn.init.constant_(self.bn2.weight, 1)
        nn.init.constant_(self.bn2.bias, 0)

    def forward(self, x):
        x = self.backbone(x)
        x = self.bn1(x)
        x = self.dropout(x)
        x = self.fc(x)
        x = self.bn2(x)
        return x # Embedding output
