"""
config.py - Centralized configuration for Herb Recognition CV project

Contains:
- Data paths and directories
- Training parameters
- Model configurations
- Hyperparameters
- Device settings
"""

import os
import torch

# =============================================================================
# DATA PATHS AND DIRECTORIES
# =============================================================================
# Change this path according to your dataset location
DATA_PATH = r"E:\Downloads\Compressed\hello\hello"

# Paths for saving models and results
SAVE_DIR = "saved_models"
MODEL_SAVE_PATH = os.path.join(SAVE_DIR, "herb_recognition_model.pth")
METADATA_PATH = os.path.join(SAVE_DIR, "model_metadata.json")
HISTORY_PATH = os.path.join(SAVE_DIR, "training_history.pkl")

# Create directory if it doesn't exist
os.makedirs(SAVE_DIR, exist_ok=True)

# =============================================================================
# TRAINING PARAMETERS
# =============================================================================
# Core training settings
EPOCHS = 50
LEARNING_RATE = 0.0001
BATCH_SIZE= 8 # Reduce if out of memory occurs
VALIDATION_SPLIT = 0.3
PATIENCE = 5  # Early stopping patience

# Optimizer settings
WEIGHT_DECAY = 0.0005
GRADIENT_CLIP_MAX_NORM = 1.0

# Learning rate scheduler settings
T_0 = 20# CosineAnnealingWarmRestarts initial restart interval
T_MULT = 2  # Multiplication factor for restart interval
ETA_MIN = 5e-7  # Minimum learning rate

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================
# Available models: "dinov2_vits14", "dinov2_vitb14", "dinov2_vitl14", "dinov2_vitg14", "custom_cnn"
MODEL_TYPE = "dinov2_vitl14"

# DINOv2 model specifications
DINOV2_CONFIGS = {
    "dinov2_vits14": {
        "embed_dim": 384,
        "description": "Small model - fastest, good for testing, <318 pixels optimal",
        "parameters": "22M"
    },
    "dinov2_vitb14": {
        "embed_dim": 768, 
        "description": "Base model - balanced performance, 224-550 pixels optimal",
        "parameters": "87M"
    },
    "dinov2_vitl14": {
        "embed_dim": 1024,
        "description": "Large model - high performance, 224-550 pixels optimal", 
        "parameters": "307M"
    },
    "dinov2_vitg14": {
        "embed_dim": 1536,
        "description": "Giant model - highest performance but very heavy, 550+ pixels optimal",
        "parameters": "1.1B"
    }
}

# Custom CNN configuration
CNN_DROPOUT_RATE = 0.3

# Classifier head configuration for DINOv2
CLASSIFIER_HIDDEN_DIM = 512
CLASSIFIER_INTERMEDIATE_DIM = 256
CLASSIFIER_DROPOUT_1 = 0.1
CLASSIFIER_DROPOUT_2 = 0.15

# =============================================================================
# IMAGE PROCESSING PARAMETERS
# =============================================================================
# Image dimensions
IMG_SIZE = (294,294)
INPUT_CHANNELS = 5

# Data augmentation parameters
ROTATION_DEGREES = 45
HORIZONTAL_FLIP_PROB = 0.5
VERTICAL_FLIP_PROB = 0.2

# ColorJitter parameters
BRIGHTNESS_FACTOR = 0.4
CONTRAST_FACTOR = 0.4
SATURATION_FACTOR = 0.3
HUE_FACTOR = 0.2

# RandomAffine parameters
TRANSLATE_FACTOR = (0.08, 0.08)
SCALE_FACTOR = (0.95, 1.15)

# Normalization parameters (ImageNet standards)
NORMALIZE_MEAN = [0.485, 0.456, 0.406]
NORMALIZE_STD = [0.229, 0.224, 0.225]

# =============================================================================
# DATA LOADING PARAMETERS
# =============================================================================
NUM_WORKERS = 0  # Set to 0 to avoid multiprocessing issues
PIN_MEMORY = True  # Enable if using GPU
SHUFFLE_TRAIN = True
SHUFFLE_VAL = False

# =============================================================================
# LOSS AND OPTIMIZATION PARAMETERS
# =============================================================================
LABEL_SMOOTHING = 0.
USE_MIXED_PRECISION = True  # Enable automatic mixed precision if supported

# =============================================================================
# DEVICE CONFIGURATION
# =============================================================================
# GPU optimization settings
CUDA_BENCHMARK = True
CUDA_DETERMINISTIC = False
ALLOW_TF32 = True

# Random seeds for reproducibility
RANDOM_SEED = 42

# =============================================================================
# VISUALIZATION PARAMETERS
# =============================================================================
SAMPLES_PER_CLASS = 5  # Number of sample images to display per class
FIGURE_SIZE_DISTRIBUTION = (12, 6)
FIGURE_SIZE_SAMPLES = (15, 3)  # Will be multiplied by number of classes
FIGURE_SIZE_TRAINING = (15, 5)
FIGURE_SIZE_CONFUSION = (10, 8)

# =============================================================================
# FILE PROCESSING PARAMETERS
# =============================================================================
# Supported image extensions
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.avif')

# Image conversion settings
JPEG_QUALITY = 98
CONVERT_AVIF_TO_JPEG = True
SAVE_OVER_ORIGINAL = True

# =============================================================================
# EVALUATION PARAMETERS
# =============================================================================
TARGET_ACCURACY = 0.98 # Target accuracy threshold
ZERO_DIVISION_HANDLING = 0  # For classification report

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_model_config(model_type):
    """
    Get configuration for specified model type
    
    Args:
        model_type (str): Model type identifier
        
    Returns:
        dict: Model configuration dictionary
    """
    if model_type in DINOV2_CONFIGS:
        return DINOV2_CONFIGS[model_type]
    elif model_type == "custom_cnn":
        return {"description": "Custom CNN architecture", "dropout_rate": CNN_DROPOUT_RATE}
    else:
        raise ValueError(f"Unknown model type: {model_type}")

def get_device():
    """
    Get the appropriate device for computation
    
    Returns:
        torch.device: The device to use for computation
    """
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    else:
        return torch.device("cpu")

def print_config():
    """
    Print current configuration settings
    """
    print("=" * 50)
    print("CURRENT CONFIGURATION")
    print("=" * 50)
    print(f"Data Path: {DATA_PATH}")
    print(f"Model Type: {MODEL_TYPE}")
    print(f"Image Size: {IMG_SIZE}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Learning Rate: {LEARNING_RATE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Device: {get_device()}")
    
    if MODEL_TYPE in DINOV2_CONFIGS:
        config = DINOV2_CONFIGS[MODEL_TYPE]
        print(f"Model Description: {config['description']}")
        print(f"Embedding Dimension: {config['embed_dim']}")
    
    print("=" * 50)