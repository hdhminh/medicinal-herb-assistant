"""
Training pipeline package for Herb Recognition CV

This package contains:
- Main training orchestration
- Model evaluation utilities
- Metrics calculation
- Visualization functions
"""

from .trainer import HerbRecognitionCV
from .evaluation import (
    evaluate_model,
    plot_training_history,
    create_confusion_matrix,
    calculate_metrics
)

__all__ = [
    'HerbRecognitionCV',
    'evaluate_model',
    'plot_training_history', 
    'create_confusion_matrix',
    'calculate_metrics'
]