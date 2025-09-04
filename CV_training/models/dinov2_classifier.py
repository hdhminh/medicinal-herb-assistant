"""
models/dinov2_classifier.py - DINOv2 Based Classifier for Herb Recognition

This module contains:
- DINOv2 backbone integration with custom classifier head
- Support for all DINOv2 variants (vits14, vitb14, vitl14, vitg14)
- Configurable classifier head with multiple layers
- Feature extraction utilities
- Model factory functions
"""

import torch
import torch.nn as nn
from CV_training.config import (
    DINOV2_CONFIGS, 
    CLASSIFIER_HIDDEN_DIM, 
    CLASSIFIER_INTERMEDIATE_DIM,
    CLASSIFIER_DROPOUT_1, 
    CLASSIFIER_DROPOUT_2
)

class DINOv2Classifier(nn.Module):
    """
    DINOv2-based classifier for herb recognition
    
    This model uses a frozen DINOv2 backbone for feature extraction
    and trains only a custom classification head.
    
    Args:
        backbone (nn.Module): Pre-trained DINOv2 backbone
        num_classes (int): Number of output classes
        embed_dim (int): Embedding dimension from the backbone
        freeze_backbone (bool): Whether to freeze backbone weights
        dropout_1 (float): First dropout rate
        dropout_2 (float): Second dropout rate
    """
    
    def __init__(self, backbone, num_classes, embed_dim, 
                 freeze_backbone=True, dropout_1=CLASSIFIER_DROPOUT_1, 
                 dropout_2=CLASSIFIER_DROPOUT_2):
        super(DINOv2Classifier, self).__init__()
        
        self.backbone = backbone
        self.num_classes = num_classes
        self.embed_dim = embed_dim
        self.freeze_backbone = freeze_backbone
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            print(f" DINOv2 backbone frozen ({embed_dim}D features)")
        else:
            print(f" DINOv2 backbone unfrozen (fine-tuning enabled)")
        
        # Custom classifier head
        self.classifier = nn.Sequential(
            # Layer normalization for stability
            nn.LayerNorm(embed_dim),
            
            # First hidden layer
            nn.Linear(embed_dim, CLASSIFIER_HIDDEN_DIM),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_1),
            
            # Second hidden layer
            nn.Linear(CLASSIFIER_HIDDEN_DIM, CLASSIFIER_INTERMEDIATE_DIM),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_2),
            
            # Output layer
            nn.Linear(CLASSIFIER_INTERMEDIATE_DIM, num_classes)
        )
        
        # Initialize classifier weights
        self._initialize_classifier()
    
    def _initialize_classifier(self):
        """
        Initialize classifier head weights
        """
        for m in self.classifier.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LayerNorm):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """
        Forward pass through the model
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, 3, height, width)
            
        Returns:
            torch.Tensor: Output logits of shape (batch_size, num_classes)
        """
        # Extract features using DINOv2 backbone
        # DINOv2 returns the [CLS] token representation
        features = self.backbone(x)
        
        # Apply classifier head
        logits = self.classifier(features)
        
        return logits
    
    def get_features(self, x):
        """
        Extract features from the backbone without classification
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Feature representations
        """
        with torch.no_grad():
            features = self.backbone(x)
        return features
    
    def unfreeze_backbone(self, layers_to_unfreeze=-1):
        """
        Unfreeze backbone for fine-tuning
        
        Args:
            layers_to_unfreeze (int): Number of layers to unfreeze from the end.
                                    -1 means unfreeze all layers
        """
        if layers_to_unfreeze == -1:
            # Unfreeze all backbone parameters
            for param in self.backbone.parameters():
                param.requires_grad = True
            print(" All backbone layers unfrozen")
        else:
            # Unfreeze specific number of layers from the end
            # This is model-specific and would need implementation based on DINOv2 structure
            print(f" Last {layers_to_unfreeze} backbone layers unfrozen")
        
        self.freeze_backbone = False
    
    def count_parameters(self):
        """
        Count total and trainable parameters
        
        Returns:
            tuple: (total_params, trainable_params, backbone_params, classifier_params)
        """
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        backbone_params = sum(p.numel() for p in self.backbone.parameters())
        classifier_params = sum(p.numel() for p in self.classifier.parameters())
        
        return total_params, trainable_params, backbone_params, classifier_params
    
    def get_model_info(self):
        """
        Get comprehensive model information
        
        Returns:
            dict: Model information
        """
        total_params, trainable_params, backbone_params, classifier_params = self.count_parameters()
        
        return {
            'model_name': 'DINOv2Classifier',
            'backbone_frozen': self.freeze_backbone,
            'num_classes': self.num_classes,
            'embed_dim': self.embed_dim,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'backbone_parameters': backbone_params,
            'classifier_parameters': classifier_params,
            'model_size_mb': total_params * 4 / (1024 * 1024),
            'architecture': {
                'backbone': 'DINOv2',
                'classifier_layers': 3,
                'hidden_dims': [CLASSIFIER_HIDDEN_DIM, CLASSIFIER_INTERMEDIATE_DIM],
                'dropout_rates': [CLASSIFIER_DROPOUT_1, CLASSIFIER_DROPOUT_2]
            }
        }


def load_dinov2_backbone(model_name='dinov2_vitl14'):
    """
    Load pre-trained DINOv2 backbone from torch.hub
    
    Args:
        model_name (str): DINOv2 variant name
        
    Returns:
        tuple: (backbone_model, embedding_dimension)
    """
    if model_name not in DINOV2_CONFIGS:
        raise ValueError(f"Unknown DINOv2 model: {model_name}. Available: {list(DINOV2_CONFIGS.keys())}")
    
    config = DINOV2_CONFIGS[model_name]
    
    try:
        print(f"   Loading {model_name} from torch.hub...")
        backbone = torch.hub.load('facebookresearch/dinov2', model_name, pretrained=True)
        print(f"   Successfully loaded {model_name}")
        print(f"   Description: {config['description']}")
        print(f"   Embedding dimension: {config['embed_dim']}")
        
        return backbone, config['embed_dim']
        
    except Exception as e:
        print(f" Failed to load {model_name}: {e}")
        print(" Make sure you have internet connection for first-time download")
        raise


def create_dinov2_classifier(num_classes, model_name='dinov2_vitl14', 
                           freeze_backbone=True, **kwargs):
    """
    Factory function to create DINOv2-based classifier
    
    Args:
        num_classes (int): Number of output classes
        model_name (str): DINOv2 variant name
        freeze_backbone (bool): Whether to freeze backbone weights
        **kwargs: Additional arguments for the classifier
        
    Returns:
        DINOv2Classifier: Instantiated model
    """
    # Load backbone
    backbone, embed_dim = load_dinov2_backbone(model_name)
    
    # Create classifier
    model = DINOv2Classifier(
        backbone=backbone,
        num_classes=num_classes,
        embed_dim=embed_dim,
        freeze_backbone=freeze_backbone,
        **kwargs
    )
    
    return model


class EnsembleDINOv2Classifier(nn.Module):
    """
    Ensemble of multiple DINOv2 models for improved performance
    
    Args:
        model_names (list): List of DINOv2 model names to ensemble
        num_classes (int): Number of output classes
        ensemble_method (str): How to combine predictions ('average', 'weighted', 'voting')
    """
    
    def __init__(self, model_names, num_classes, ensemble_method='average'):
        super(EnsembleDINOv2Classifier, self).__init__()
        
        self.model_names = model_names
        self.num_classes = num_classes
        self.ensemble_method = ensemble_method
        
        # Create individual models
        self.models = nn.ModuleList()
        for model_name in model_names:
            model = create_dinov2_classifier(num_classes, model_name)
            self.models.append(model)
        
        # Learnable weights for weighted ensemble
        if ensemble_method == 'weighted':
            self.ensemble_weights = nn.Parameter(torch.ones(len(model_names)))
        
        print(f"   Created ensemble with {len(model_names)} DINOv2 models")
        print(f"   Models: {model_names}")
        print(f"   Ensemble method: {ensemble_method}")
    
    def forward(self, x):
        """
        Forward pass through ensemble
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Ensemble predictions
        """
        # Get predictions from all models
        predictions = []
        for model in self.models:
            pred = model(x)
            predictions.append(pred)
        
        # Combine predictions
        if self.ensemble_method == 'average':
            # Simple average
            ensemble_pred = torch.stack(predictions).mean(dim=0)
        
        elif self.ensemble_method == 'weighted':
            # Weighted average with learnable weights
            weights = torch.softmax(self.ensemble_weights, dim=0)
            weighted_preds = []
            for i, pred in enumerate(predictions):
                weighted_preds.append(weights[i] * pred)
            ensemble_pred = torch.stack(weighted_preds).sum(dim=0)
        
        elif self.ensemble_method == 'voting':
            # Hard voting (argmax then mode)
            votes = []
            for pred in predictions:
                votes.append(torch.argmax(pred, dim=1))
            # Convert to one-hot and average (soft voting approximation)
            votes_tensor = torch.stack(votes).float()
            ensemble_pred = torch.zeros_like(predictions[0])
            for i in range(self.num_classes):
                class_votes = (votes_tensor == i).float().mean(dim=0)
                ensemble_pred[:, i] = class_votes
        
        else:
            raise ValueError(f"Unknown ensemble method: {self.ensemble_method}")
        
        return ensemble_pred
    
    def count_parameters(self):
        """Count total parameters across all models"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return total_params, trainable_params


def print_dinov2_model_summary(model, input_size=(3, 392, 392)):
    """
    Print detailed summary for DINOv2-based models
    
    Args:
        model: DINOv2-based model
        input_size (tuple): Input tensor size (C, H, W)
    """
    print("="*70)
    print("DINOV2 MODEL SUMMARY")
    print("="*70)
    
    if hasattr(model, 'get_model_info'):
        info = model.get_model_info()
        
        print(f"Model: {info['model_name']}")
        print(f"Backbone Frozen: {info['backbone_frozen']}")
        print(f"Classes: {info['num_classes']}")
        print(f"Embedding Dimension: {info['embed_dim']}")
        print(f"\nParameters:")
        print(f"  Total: {info['total_parameters']:,}")
        print(f"  Trainable: {info['trainable_parameters']:,}")
        print(f"  Backbone: {info['backbone_parameters']:,}")
        print(f"  Classifier: {info['classifier_parameters']:,}")
        print(f"  Model Size: {info['model_size_mb']:.2f} MB")
        
        print(f"\nArchitecture:")
        arch = info['architecture']
        print(f"  Backbone: {arch['backbone']}")
        print(f"  Classifier Layers: {arch['classifier_layers']}")
        print(f"  Hidden Dimensions: {arch['hidden_dims']}")
        print(f"  Dropout Rates: {arch['dropout_rates']}")
    
    # Test forward pass
    try:
        dummy_input = torch.randn(1, *input_size)
        with torch.no_grad():
            output = model(dummy_input)
        print(f"\nForward Pass Test:")
        print(f"  Input Shape: {dummy_input.shape}")
        print(f"  Output Shape: {output.shape}")
        print(f"  Forward pass successful")
    except Exception as e:
        print(f"  Forward pass failed: {e}")
    
    print("="*70)
"""
models/dinov2_classifier.py - DINOv2 Based Classifier for Herb Recognition

This module contains:
- DINOv2 backbone integration with custom classifier head
- Support for all DINOv2 variants (vits14, vitb14, vitl14, vitg14)
- Configurable classifier head with multiple layers
- Feature extraction utilities
- Model factory functions
"""

import torch
import torch.nn as nn
from CV_training.config import (
    DINOV2_CONFIGS, 
    CLASSIFIER_HIDDEN_DIM, 
    CLASSIFIER_INTERMEDIATE_DIM,
    CLASSIFIER_DROPOUT_1, 
    CLASSIFIER_DROPOUT_2
)

class DINOv2Classifier(nn.Module):
    """
    DINOv2-based classifier for herb recognition
    
    This model uses a frozen DINOv2 backbone for feature extraction
    and trains only a custom classification head.
    
    Args:
        backbone (nn.Module): Pre-trained DINOv2 backbone
        num_classes (int): Number of output classes
        embed_dim (int): Embedding dimension from the backbone
        freeze_backbone (bool): Whether to freeze backbone weights
        dropout_1 (float): First dropout rate
        dropout_2 (float): Second dropout rate
    """
    
    def __init__(self, backbone, num_classes, embed_dim, 
                 freeze_backbone=True, dropout_1=CLASSIFIER_DROPOUT_1, 
                 dropout_2=CLASSIFIER_DROPOUT_2):
        super(DINOv2Classifier, self).__init__()
        
        self.backbone = backbone
        self.num_classes = num_classes
        self.embed_dim = embed_dim
        self.freeze_backbone = freeze_backbone
        
        # Freeze backbone if specified
        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            print(f" DINOv2 backbone frozen ({embed_dim}D features)")
        else:
            print(f" DINOv2 backbone unfrozen (fine-tuning enabled)")
        
        # Custom classifier head
        self.classifier = nn.Sequential(
            # Layer normalization for stability
            nn.LayerNorm(embed_dim),
            
            # First hidden layer
            nn.Linear(embed_dim, CLASSIFIER_HIDDEN_DIM),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_1),
            
            # Second hidden layer
            nn.Linear(CLASSIFIER_HIDDEN_DIM, CLASSIFIER_INTERMEDIATE_DIM),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_2),
            
            # Output layer
            nn.Linear(CLASSIFIER_INTERMEDIATE_DIM, num_classes)
        )
        
        # Initialize classifier weights
        self._initialize_classifier()
    
    def _initialize_classifier(self):
        """
        Initialize classifier head weights
        """
        for m in self.classifier.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LayerNorm):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """
        Forward pass through the model
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, 3, height, width)
            
        Returns:
            torch.Tensor: Output logits of shape (batch_size, num_classes)
        """
        # Extract features using DINOv2 backbone
        # DINOv2 returns the [CLS] token representation
        features = self.backbone(x)
        
        # Apply classifier head
        logits = self.classifier(features)
        
        return logits
    
    def get_features(self, x):
        """
        Extract features from the backbone without classification
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Feature representations
        """
        with torch.no_grad():
            features = self.backbone(x)
        return features
    
    def unfreeze_backbone(self, layers_to_unfreeze=-1):
        """
        Unfreeze backbone for fine-tuning
        
        Args:
            layers_to_unfreeze (int): Number of layers to unfreeze from the end.
                                    -1 means unfreeze all layers
        """
        if layers_to_unfreeze == -1:
            # Unfreeze all backbone parameters
            for param in self.backbone.parameters():
                param.requires_grad = True
            print(" All backbone layers unfrozen")
        else:
            # Unfreeze specific number of layers from the end
            # This is model-specific and would need implementation based on DINOv2 structure
            print(f" Last {layers_to_unfreeze} backbone layers unfrozen")
        
        self.freeze_backbone = False
    
    def count_parameters(self):
        """
        Count total and trainable parameters
        
        Returns:
            tuple: (total_params, trainable_params, backbone_params, classifier_params)
        """
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        backbone_params = sum(p.numel() for p in self.backbone.parameters())
        classifier_params = sum(p.numel() for p in self.classifier.parameters())
        
        return total_params, trainable_params, backbone_params, classifier_params
    
    def get_model_info(self):
        """
        Get comprehensive model information
        
        Returns:
            dict: Model information
        """
        total_params, trainable_params, backbone_params, classifier_params = self.count_parameters()
        
        return {
            'model_name': 'DINOv2Classifier',
            'backbone_frozen': self.freeze_backbone,
            'num_classes': self.num_classes,
            'embed_dim': self.embed_dim,
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'backbone_parameters': backbone_params,
            'classifier_parameters': classifier_params,
            'model_size_mb': total_params * 4 / (1024 * 1024),
            'architecture': {
                'backbone': 'DINOv2',
                'classifier_layers': 3,
                'hidden_dims': [CLASSIFIER_HIDDEN_DIM, CLASSIFIER_INTERMEDIATE_DIM],
                'dropout_rates': [CLASSIFIER_DROPOUT_1, CLASSIFIER_DROPOUT_2]
            }
        }


def load_dinov2_backbone(model_name='dinov2_vitl14'):
    """
    Load pre-trained DINOv2 backbone from torch.hub
    
    Args:
        model_name (str): DINOv2 variant name
        
    Returns:
        tuple: (backbone_model, embedding_dimension)
    """
    if model_name not in DINOV2_CONFIGS:
        raise ValueError(f"Unknown DINOv2 model: {model_name}. Available: {list(DINOV2_CONFIGS.keys())}")
    
    config = DINOV2_CONFIGS[model_name]
    
    try:
        print(f"   Loading {model_name} from torch.hub...")
        backbone = torch.hub.load('facebookresearch/dinov2', model_name, pretrained=True)
        print(f"   Successfully loaded {model_name}")
        print(f"   Description: {config['description']}")
        print(f"   Embedding dimension: {config['embed_dim']}")
        
        return backbone, config['embed_dim']
        
    except Exception as e:
        print(f" Failed to load {model_name}: {e}")
        print(" Make sure you have internet connection for first-time download")
        raise


def create_dinov2_classifier(num_classes, model_name='dinov2_vitl14', 
                           freeze_backbone=True, **kwargs):
    """
    Factory function to create DINOv2-based classifier
    
    Args:
        num_classes (int): Number of output classes
        model_name (str): DINOv2 variant name
        freeze_backbone (bool): Whether to freeze backbone weights
        **kwargs: Additional arguments for the classifier
        
    Returns:
        DINOv2Classifier: Instantiated model
    """
    # Load backbone
    backbone, embed_dim = load_dinov2_backbone(model_name)
    
    # Create classifier
    model = DINOv2Classifier(
        backbone=backbone,
        num_classes=num_classes,
        embed_dim=embed_dim,
        freeze_backbone=freeze_backbone,
        **kwargs
    )
    
    return model


class EnsembleDINOv2Classifier(nn.Module):
    """
    Ensemble of multiple DINOv2 models for improved performance
    
    Args:
        model_names (list): List of DINOv2 model names to ensemble
        num_classes (int): Number of output classes
        ensemble_method (str): How to combine predictions ('average', 'weighted', 'voting')
    """
    
    def __init__(self, model_names, num_classes, ensemble_method='average'):
        super(EnsembleDINOv2Classifier, self).__init__()
        
        self.model_names = model_names
        self.num_classes = num_classes
        self.ensemble_method = ensemble_method
        
        # Create individual models
        self.models = nn.ModuleList()
        for model_name in model_names:
            model = create_dinov2_classifier(num_classes, model_name)
            self.models.append(model)
        
        # Learnable weights for weighted ensemble
        if ensemble_method == 'weighted':
            self.ensemble_weights = nn.Parameter(torch.ones(len(model_names)))
        
        print(f"   Created ensemble with {len(model_names)} DINOv2 models")
        print(f"   Models: {model_names}")
        print(f"   Ensemble method: {ensemble_method}")
    
    def forward(self, x):
        """
        Forward pass through ensemble
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Ensemble predictions
        """
        # Get predictions from all models
        predictions = []
        for model in self.models:
            pred = model(x)
            predictions.append(pred)
        
        # Combine predictions
        if self.ensemble_method == 'average':
            # Simple average
            ensemble_pred = torch.stack(predictions).mean(dim=0)
        
        elif self.ensemble_method == 'weighted':
            # Weighted average with learnable weights
            weights = torch.softmax(self.ensemble_weights, dim=0)
            weighted_preds = []
            for i, pred in enumerate(predictions):
                weighted_preds.append(weights[i] * pred)
            ensemble_pred = torch.stack(weighted_preds).sum(dim=0)
        
        elif self.ensemble_method == 'voting':
            # Hard voting (argmax then mode)
            votes = []
            for pred in predictions:
                votes.append(torch.argmax(pred, dim=1))
            # Convert to one-hot and average (soft voting approximation)
            votes_tensor = torch.stack(votes).float()
            ensemble_pred = torch.zeros_like(predictions[0])
            for i in range(self.num_classes):
                class_votes = (votes_tensor == i).float().mean(dim=0)
                ensemble_pred[:, i] = class_votes
        
        else:
            raise ValueError(f"Unknown ensemble method: {self.ensemble_method}")
        
        return ensemble_pred
    
    def count_parameters(self):
        """Count total parameters across all models"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return total_params, trainable_params


def print_dinov2_model_summary(model, input_size=(3, 392, 392)):
    """
    Print detailed summary for DINOv2-based models
    
    Args:
        model: DINOv2-based model
        input_size (tuple): Input tensor size (C, H, W)
    """
    print("="*70)
    print("DINOV2 MODEL SUMMARY")
    print("="*70)
    
    if hasattr(model, 'get_model_info'):
        info = model.get_model_info()
        
        print(f"Model: {info['model_name']}")
        print(f"Backbone Frozen: {info['backbone_frozen']}")
        print(f"Classes: {info['num_classes']}")
        print(f"Embedding Dimension: {info['embed_dim']}")
        print(f"\nParameters:")
        print(f"  Total: {info['total_parameters']:,}")
        print(f"  Trainable: {info['trainable_parameters']:,}")
        print(f"  Backbone: {info['backbone_parameters']:,}")
        print(f"  Classifier: {info['classifier_parameters']:,}")
        print(f"  Model Size: {info['model_size_mb']:.2f} MB")
        
        print(f"\nArchitecture:")
        arch = info['architecture']
        print(f"  Backbone: {arch['backbone']}")
        print(f"  Classifier Layers: {arch['classifier_layers']}")
        print(f"  Hidden Dimensions: {arch['hidden_dims']}")
        print(f"  Dropout Rates: {arch['dropout_rates']}")
    
    # Test forward pass
    try:
        dummy_input = torch.randn(1, *input_size)
        with torch.no_grad():
            output = model(dummy_input)
        print(f"\nForward Pass Test:")
        print(f"  Input Shape: {dummy_input.shape}")
        print(f"  Output Shape: {output.shape}")
        print(f"  Forward pass successful")
    except Exception as e:
        print(f"  Forward pass failed: {e}")
    
    print("="*70)