import torch
import torch.nn as nn
import torch.nn.functional as F

class HerbCNN(nn.Module):
    def __init__(self, num_classes=10):  # thêm num_classes
        super(HerbCNN, self).__init__()
        
        # Convolution layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)

        # Fully connected layers
        self.fc1 = nn.Linear(64 * 56 * 56, 128)  # nếu input là 224x224
        self.fc2 = nn.Linear(128, num_classes)   # số lớp output linh động

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
