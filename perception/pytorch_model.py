import torch
import torch.nn as nn

class AVPerceptionModel(nn.Module):
    def __init__(self):
        super(AVPerceptionModel, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.fc = nn.Linear(32 * 6 * 6, 3)  # obstacle, pedestrian, vehicle

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)
