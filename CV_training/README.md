# 🌿 Herb Recognition Computer Vision System

A comprehensive deep learning pipeline for classifying herb images using state-of-the-art computer vision models, including DINOv2 and custom CNN architectures.

## Features

- **Multiple Model Architectures**: Support for DINOv2 (vits14, vitb14, vitl14, vitg14) and custom CNN models
- **Robust Image Loading**: Handles various formats including AVIF with automatic conversion
- **Advanced Data Augmentation**: Comprehensive augmentation pipeline for improved generalization
- **Memory Efficient**: Optimized data loading with caching for large datasets
- **GPU Acceleration**: Full CUDA support with optimization flags
- **Comprehensive Evaluation**: Detailed metrics, confusion matrices, and visualization
- **Modular Architecture**: Clean, maintainable code structure with separate modules

## Project Structure

```
herb_recognition_cv/
├── main.py                    # Main entry point
├── config.py                  # Configuration management
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── gpu_setup.py          # GPU configuration
│   ├── image_utils.py        # Image processing utilities
│   └── data_utils.py         # Data processing utilities
├── models/                    # Model architectures
│   ├── __init__.py
│   ├── herb_cnn.py           # Custom CNN implementation
│   └── dinov2_classifier.py  # DINOv2 based models
├── data/                     # Data handling
│   ├── __init__.py
│   ├── dataset.py            # Dataset implementation
│   └── data_loader.py        # Data loading utilities
├── training/                 # Training pipeline
│   ├── __init__.py
│   ├── trainer.py            # Main training class
│   └── evaluation.py         # Evaluation and metrics
└── saved_models/             # Model outputs
    └── .gitkeep
```

## Installation

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended)
- 8GB+ RAM
- 10GB+ free disk space

### Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd herb_recognition_cv
```

2. **Create virtual environment**

```bash
python -m venv herb_cv_env
source herb_cv_env/bin/activate  # Linux/Mac
# or
herb_cv_env\Scripts\activate  # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Verify installation**

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

## Dataset Setup

### Expected Directory Structure

Your dataset should be organized as follows:

```
your_dataset/
├── class_1/
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── class_2/
│   ├── image1.jpg
│   ├── image2.avif
│   └── ...
└── class_n/
    └── ...
```

### Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff, .tif)
- AVIF (.avif) - automatically converted to JPEG

## Configuration

Edit `config.py` to customize your setup:

```python
# Data configuration
DATA_PATH = "path/to/your/dataset"
IMG_SIZE = (392, 392)
BATCH_SIZE = 16

# Model configuration
MODEL_TYPE = "dinov2_vitl14"  # or "dinov2_vits14", "custom_cnn", etc.

# Training configuration
EPOCHS = 50
LEARNING_RATE = 0.0005
VALIDATION_SPLIT = 0.3
```

## Usage

### Basic Usage

Run the complete pipeline with default settings:

```bash
python main.py
```

### Advanced Usage

```bash
# Use different model
python main.py --model dinov2_vitb14

# Custom data path
python main.py --data-path /path/to/dataset

# Quick test with reduced parameters
python main.py --quick-test

# Dry run (analysis only, no training)
python main.py --dry-run

# Custom training parameters
python main.py --epochs 100 --lr 0.001 --batch-size 32
```

### Command Line Options

| Option              | Description               | Default         |
| ------------------- | ------------------------- | --------------- |
| `--data-path`       | Path to dataset directory | From config     |
| `--model`           | Model architecture        | `dinov2_vitl14` |
| `--epochs`          | Number of training epochs | 50              |
| `--lr`              | Learning rate             | 0.0005          |
| `--batch-size`      | Batch size                | 16              |
| `--patience`        | Early stopping patience   | 7               |
| `--quick-test`      | Quick test mode           | False           |
| `--dry-run`         | Analysis only             | False           |
| `--skip-conversion` | Skip AVIF conversion      | False           |

## Model Architectures

### DINOv2 Models

| Model           | Parameters | Best For             | Memory    |
| --------------- | ---------- | -------------------- | --------- |
| `dinov2_vits14` | 22M        | Quick experiments    | Low       |
| `dinov2_vitb14` | 87M        | Balanced performance | Medium    |
| `dinov2_vitl14` | 307M       | High accuracy        | High      |
| `dinov2_vitg14` | 1.1B       | Maximum performance  | Very High |

### Custom CNN

- Lightweight custom architecture
- 4 convolutional blocks
- Global average pooling
- ~2M parameters

## Training Pipeline

The training pipeline includes:

1. **Data Preprocessing**

   - AVIF format detection and conversion
   - Dataset structure analysis
   - Image validation

2. **Data Augmentation**

   - Random rotation (±45°)
   - Horizontal/vertical flips
   - Color jittering
   - Random affine transformations

3. **Training Features**

   - Early stopping with patience
   - Learning rate scheduling
   - Gradient clipping
   - Mixed precision training
   - Comprehensive logging

4. **Evaluation**
   - Accuracy metrics
   - Confusion matrix
   - Per-class performance
   - Training history visualization

## Output Files

After training, the following files are generated:

- `saved_models/herb_recognition_model.pth` - Trained model weights
- `saved_models/model_metadata.json` - Model configuration and metrics
- `saved_models/training_history.pkl` - Training history for analysis

## Troubleshooting

### Common Issues

**CUDA Out of Memory**

```bash
# Reduce batch size
python main.py --batch-size 8

# Use smaller model
python main.py --model dinov2_vits14
```

**AVIF Loading Issues**

```bash
# Install additional dependencies
pip install pillow-avif imageio
```

**Slow Training on CPU**

```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Performance Optimization

1. **For Small Datasets (< 1000 images)**

   - Use `dinov2_vits14` or `custom_cnn`
   - Increase data augmentation
   - Reduce batch size to 8-16

2. **For Large Datasets (> 10,000 images)**

   - Use `dinov2_vitl14` or `dinov2_vitg14`
   - Increase batch size to 32-64
   - Enable memory-efficient dataset

3. **For Limited GPU Memory**
   - Use gradient accumulation
   - Reduce image size to (224, 224)
   - Use mixed precision training

## Extending the System

### Adding New Models

1. Create model in `models/` directory
2. Add to `config.py` model choices
3. Implement in training pipeline

### Custom Data Augmentation

Modify transforms in `data/data_loader.py`:

```python
custom_transform = transforms.Compose([
    transforms.Resize((392, 392)),
    # Add your custom transforms here
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

### Custom Loss Functions

Implement in `training/trainer.py`:

```python
# Example: Focal Loss for imbalanced datasets
class FocalLoss(nn.Module):
    def __init__(self, alpha=1, gamma=2):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        # Implementation here
        pass
```

## API Reference

### Key Classes

- `HerbDataset`: Custom dataset class with robust image loading
- `HerbCNN`: Custom CNN architecture
- `DINOv2Classifier`: DINOv2-based classifier
- `HerbRecognitionCV`: Main training and evaluation pipeline

### Configuration Options

See `config.py` for all available configuration parameters.

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [DINOv2](https://github.com/facebookresearch/dinov2) by Meta AI
- [PyTorch](https://pytorch.org/) team
- [Torchvision](https://pytorch.org/vision/) contributors

## 📞 Support

For questions and support:

1. Check the troubleshooting section
2. Review closed issues
3. Open a new issue with detailed description

---

**Happy Herb Recognition! 🌿**
