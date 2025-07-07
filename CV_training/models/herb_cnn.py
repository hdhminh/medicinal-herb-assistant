"""
models/herb_cnn.py - Custom CNN Architecture for Herb Recognition

This module contains:
- Custom CNN architecture designed for herb classification
- Modern architectural components (BatchNorm, Dropout, Global Average Pooling)
- Configurable dropout rates and layer dimensions
- Efficient feature extraction with progressive channel increase
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from config import CNN_DROPOUT_RATE

class HerbCNN(nn.Module):
    """
    Custom CNN architecture for herb recognition
    
    Architecture Features:
    - 4 convolutional blocks with progressive channel increase (32 → 64 → 128 → 256)
    - BatchNormalization for training stability
    - Dropout for regularization
    - Global Average Pooling to reduce parameters
    - Multi-layer classifier with residual-like connections
    
    Args:
        num_classes (int): Number of herb classes to classify
        dropout_rate (float): Dropout probability for regularization
        input_channels (int): Number of input channels (default: 3 for RGB)
    """
    
    def __init__(self, num_classes, dropout_rate=CNN_DROPOUT_RATE, input_channels=3):
        super(HerbCNN, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # First Convolutional Block (3 → 32 channels)
        self.conv1 = nn.Sequential(
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 392x392 → 196x196
            nn.Dropout2d(0.25)
        )
        
        # Second Convolutional Block (32 → 64 channels)
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 196x196 → 98x98
            nn.Dropout2d(0.25)
        )
        
        # Third Convolutional Block (64 → 128 channels)
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 98x98 → 49x49
            nn.Dropout2d(0.25)
        )
        
        # Fourth Convolutional Block (128 → 256 channels)
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),  # 49x49 → 24x24
            nn.Dropout2d(0.25)
        )
        
        # Global Average Pooling (reduces parameters significantly)
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Classifier Head with multiple layers
        self.classifier = nn.Sequential(
            # First classifier layer
            nn.Linear(256, 512, bias=False),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            
            # Second classifier layer
            nn.Linear(512, 256, bias=False),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            
            # Output layer
            nn.Linear(256, num_classes)
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """
        Initialize network weights using modern best practices
        """
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                # He initialization for ReLU activations
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d) or isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                # Xavier initialization for linear layers
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """
        Forward pass through the network
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, 3, height, width)
            
        Returns:
            torch.Tensor: Output logits of shape (batch_size, num_classes)
        """
        # Convolutional feature extraction
        x = self.conv1(x)  # (batch, 32, 196, 196)
        x = self.conv2(x)  # (batch, 64, 98, 98)
        x = self.conv3(x)  # (batch, 128, 49, 49)
        x = self.conv4(x)  # (batch, 256, 24, 24)
        
        # Global average pooling
        x = self.global_avg_pool(x)  # (batch, 256, 1, 1)
        x = x.view(x.size(0), -1)    # (batch, 256) - Flatten
        
        # Classification
        x = self.classifier(x)  # (batch, num_classes)
        
        return x
    
    def get_feature_maps(self, x, layer_name='conv4'):
        """
        Extract feature maps from intermediate layers for visualization
        
        Args:
            x (torch.Tensor): Input tensor
            layer_name (str): Layer to extract features from ('conv1', 'conv2', 'conv3', 'conv4')
            
        Returns:
            torch.Tensor: Feature maps from the specified layer
        """
        with torch.no_grad():
            if layer_name == 'conv1':
                return self.conv1(x)
            elif layer_name == 'conv2':
                x = self.conv1(x)
                return self.conv2(x)
            elif layer_name == 'conv3':
                x = self.conv1(x)
                x = self.conv2(x)
                return self.conv3(x)
            elif layer_name == 'conv4':
                x = self.conv1(x)
                x = self.conv2(x)
                x = self.conv3(x)
                return self.conv4(x)
            else:
                raise ValueError(f"Unknown layer name: {layer_name}")
    
    def count_parameters(self):
        """
        Count total and trainable parameters
        
        Returns:
            tuple: (total_params, trainable_params)
        """
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return total_params, trainable_params
    
    def get_model_info(self):
        """
        Get comprehensive model information
        
        Returns:
            dict: Model information including architecture details
        """
        total_params, trainable_params = self.count_parameters()
        
        return {
            'model_name': 'HerbCNN',
            'num_classes': self.num_classes,
            'dropout_rate': self.dropout_rate,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'model_size_mb': total_params * 4 / (1024 * 1024),  # Assuming float32
            'architecture': {
                'conv_blocks': 4,
                'channels': [32, 64, 128, 256],
                'pooling': 'AdaptiveAvgPool2d',
                'classifier_layers': 3,
                'regularization': ['BatchNorm', 'Dropout']
            }
        }


class LightweightHerbCNN(nn.Module):
    """
    Lightweight version of HerbCNN for faster inference and smaller memory footprint
    
    Reduced parameters while maintaining accuracy:
    - Fewer channels per layer
    - Depthwise separable convolutions
    - More aggressive pooling
    
    Args:
        num_classes (int): Number of herb classes to classify
        dropout_rate (float): Dropout probability for regularization
    """
    
    def __init__(self, num_classes, dropout_rate=0.2):
        super(LightweightHerbCNN, self).__init__()
        
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        
        # Depthwise Separable Convolution Helper
        def depthwise_separable_conv(in_channels, out_channels, stride=1):
            return nn.Sequential(
                # Depthwise convolution
                nn.Conv2d(in_channels, in_channels, kernel_size=3, stride=stride, 
                         padding=1, groups=in_channels, bias=False),
                nn.BatchNorm2d(in_channels),
                nn.ReLU(inplace=True),
                
                # Pointwise convolution
                nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(inplace=True)
            )
        
        # Feature extraction backbone
        self.features = nn.Sequential(
            # Initial convolution
            nn.Conv2d(3, 24, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(24),
            nn.ReLU(inplace=True),
            
            # Depthwise separable blocks
            depthwise_separable_conv(24, 48),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.1),
            
            depthwise_separable_conv(48, 96),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.1),
            
            depthwise_separable_conv(96, 192),
            nn.MaxPool2d(2),
            nn.Dropout2d(0.1),
            
            # Final convolution
            nn.Conv2d(192, 256, kernel_size=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
        )
        
        # Global average pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Lightweight classifier
        self.classifier = nn.Sequential(
            nn.Linear(256, 128, bias=False),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_classes)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights using He and Xavier initialization"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d) or isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """Forward pass through the lightweight network"""
        x = self.features(x)
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x
    
    def count_parameters(self):
        """Count total and trainable parameters"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return total_params, trainable_params


def create_herb_cnn(num_classes, model_variant='standard', **kwargs):
    """
    Factory function to create HerbCNN models
    
    Args:
        num_classes (int): Number of classes for classification
        model_variant (str): Model variant ('standard', 'lightweight')
        **kwargs: Additional arguments passed to model constructor
        
    Returns:
        nn.Module: Instantiated model
    """
    if model_variant == 'standard':
        return HerbCNN(num_classes, **kwargs)
    elif model_variant == 'lightweight':
        return LightweightHerbCNN(num_classes, **kwargs)
    else:
        raise ValueError(f"Unknown model variant: {model_variant}")


def print_model_summary(model, input_size=(3, 392, 392)):
    """
    Print detailed model summary
    
    Args:
        model (nn.Module): Model to summarize
        input_size (tuple): Input tensor size (C, H, W)
    """
    print("="*60)
    print("MODEL ARCHITECTURE SUMMARY")
    print("="*60)
    
    # Get model info
    if hasattr(model, 'get_model_info'):
        info = model.get_model_info()
        print(f"Model: {info['model_name']}")
        print(f"Classes: {info['num_classes']}")
        print(f"Total Parameters: {info['total_parameters']:,}")
        print(f"Trainable Parameters: {info['trainable_parameters']:,}")
        print(f"Model Size: {info['model_size_mb']:.2f} MB")
    else:
        total_params, trainable_params = model.count_parameters()
        print(f"Model: {model.__class__.__name__}")
        print(f"Total Parameters: {total_params:,}")
        print(f"Trainable Parameters: {trainable_params:,}")
        print(f"Model Size: {total_params * 4 / (1024 * 1024):.2f} MB")
    
    # Test forward pass
    try:
        dummy_input = torch.randn(1, *input_size)
        with torch.no_grad():
            output = model(dummy_input)
        print(f"Input Shape: {dummy_input.shape}")
        print(f"Output Shape: {output.shape}")
    except Exception as e:
        print(f"Forward pass test failed: {e}")
    
    print("="*60)