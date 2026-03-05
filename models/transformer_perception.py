import torch
import torch.nn as nn

class PatchEmbedding(nn.Module):
    def __init__(self, img_size=224, patch_size=16, emb_dim=256):
        super().__init__()
        self.proj = nn.Conv2d(3, emb_dim, kernel_size=patch_size, stride=patch_size)

    def forward(self, x):
        x = self.proj(x)
        x = x.flatten(2).transpose(1, 2)
        return x


class TransformerPerception(nn.Module):
    def __init__(self, emb_dim=256, num_heads=8, num_layers=4, num_classes=5):
        super().__init__()
        self.patch_embed = PatchEmbedding()
        encoder_layer = nn.TransformerEncoderLayer(d_model=emb_dim, nhead=num_heads)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.cls_head = nn.Linear(emb_dim, num_classes)

    def forward(self, x):
        x = self.patch_embed(x)
        x = self.transformer(x)
        x = x.mean(dim=1)
        return self.cls_head(x)
