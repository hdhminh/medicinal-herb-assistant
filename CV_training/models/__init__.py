"""
Model architectures package for Herb Recognition CV

This package contains:
- Custom CNN implementations
- DINOv2-based classifiers
- Model factory functions
- Model utilities
"""

from .herb_cnn import HerbCNN, LightweightHerbCNN, create_herb_cnn, print_model_summary
from .dinov2_classifier import (
    DINOv2Classifier, 
    create_dinov2_classifier, 
    load_dinov2_backbone,
    print_dinov2_model_summary
)

__all__ = [
    'HerbCNN',
    'LightweightHerbCNN', 
    'create_herb_cnn',
    'print_model_summary',
    'DINOv2Classifier',
    'create_dinov2_classifier',
    'load_dinov2_backbone',
    'print_dinov2_model_summary'
]