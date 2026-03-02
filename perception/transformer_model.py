import torch
import torch.nn as nn
from torchvision.models import vit_b_16

class AVTransformerModel(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        self.model = vit_b_16(pretrained=True)
        self.model.heads.head = nn.Linear(self.model.heads.head.in_features, num_classes)

    def forward(self, x):
        return self.model(x)
