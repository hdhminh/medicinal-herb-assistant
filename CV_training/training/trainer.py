"""
training/trainer.py - Main Training Class for Herb Recognition CV

This module contains:
- HerbRecognitionCV: Main training orchestration class
- Complete training pipeline with monitoring
- Model building and configuration
- Data loading and preprocessing coordination
- Training loop with early stopping and scheduling
- Model saving and loading utilities
"""

import os
import json
import pickle
import time
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tqdm import tqdm

from utils.gpu_setup import get_device
from utils.data_utils import analyze_dataset_structure, visualize_class_distribution
from data.data_loader import create_data_loaders
from models.herb_cnn import create_herb_cnn
from models.dinov2_classifier import create_dinov2_classifier
from training.evaluation import evaluate_model, plot_training_history
from config import *

class HerbRecognitionCV:
    """
    Main training and evaluation system for herb recognition
    
    This class orchestrates the complete machine learning pipeline including:
    - Dataset exploration and analysis
    - Data loading with augmentation
    - Model creation and configuration
    - Training with monitoring and early stopping
    - Evaluation and visualization
    - Model persistence and metadata management
    
    Args:
        data_path (str): Path to dataset directory
        img_size (tuple): Target image dimensions
        batch_size (int): Batch size for training
        num_workers (int): Number of data loading workers
    """
    
    def __init__(self, data_path, img_size=IMG_SIZE, batch_size=BATCH_SIZE, num_workers=NUM_WORKERS):
        self.data_path = data_path
        self.img_size = img_size
        self.batch_size = batch_size
        self.num_workers = num_workers
        
        # Initialize core components
        self.device = get_device()
        self.model = None
        self.class_names = []
        self.num_classes = 0
        self.class_to_idx = {}
        
        # Training components
        self.train_loader = None
        self.val_loader = None
        self.test_loader = None
        
        # Training history and metrics
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
            'learning_rates': []
        }
        
        # Training state
        self.best_val_acc = 0.0
        self.best_model_state = None
        self.training_start_time = None
        
        print(f"🌿 HerbRecognitionCV initialized")
        print(f"   Device: {self.device}")
        print(f"   Data path: {data_path}")
        print(f"   Image size: {img_size}")
        print(f"   Batch size: {batch_size}")
    
    def explore_dataset(self):
        """
        Explore and analyze the dataset structure
        
        Returns:
            dict: Dataset analysis results
        """
        print("\n" + "="*60)
        print("DATASET EXPLORATION")
        print("="*60)
        
        # Analyze dataset structure
        analysis = analyze_dataset_structure(self.data_path, verbose=True)
        
        # Update class information
        self.class_names = analysis['class_names']
        self.num_classes = analysis['total_classes']
        self.class_to_idx = {name: idx for idx, name in enumerate(self.class_names)}
        
        # Visualize class distribution
        print(f"\nVisualizing class distribution...")
        visualize_class_distribution(analysis['class_counts'])
        
        return analysis['class_counts']
    
    def visualize_samples(self, samples_per_class=SAMPLES_PER_CLASS):
        """
        Visualize sample images from each class
        
        Args:
            samples_per_class (int): Number of sample images per class
        """
        import matplotlib.pyplot as plt
        from utils.image_utils import load_image_robust
        
        print(f"\nVisualizing {samples_per_class} samples per class...")
        
        fig, axes = plt.subplots(
            len(self.class_names), 
            samples_per_class, 
            figsize=(samples_per_class * 3, len(self.class_names) * 2.5)
        )
        
        if len(self.class_names) == 1:
            axes = axes.reshape(1, -1)
        if samples_per_class == 1:
            axes = axes.reshape(-1, 1)
        
        for i, class_name in enumerate(self.class_names):
            class_path = os.path.join(self.data_path, class_name)
            
            # Get image files
            image_files = [f for f in os.listdir(class_path) 
                          if f.lower().endswith(SUPPORTED_EXTENSIONS)]
            
            # Select random samples
            if len(image_files) >= samples_per_class:
                selected_files = np.random.choice(image_files, samples_per_class, replace=False)
            else:
                selected_files = image_files
            
            for j, img_file in enumerate(selected_files):
                if j >= samples_per_class:
                    break
                    
                img_path = os.path.join(class_path, img_file)
                
                try:
                    img = load_image_robust(img_path)
                    if img is None:
                        # Create placeholder
                        img = plt.imread(np.zeros((100, 100, 3), dtype=np.uint8))
                    else:
                        img = img.resize(self.img_size)
                    
                    ax = axes[i, j] if len(self.class_names) > 1 else axes[j]
                    ax.imshow(img)
                    ax.set_title(f"{class_name}", fontsize=10)
                    ax.axis('off')
                    
                except Exception as e:
                    print(f"   Could not display {img_file}: {e}")
                    
                    ax = axes[i, j] if len(self.class_names) > 1 else axes[j]
                    ax.text(0.5, 0.5, 'Error\nLoading\nImage', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(f"{class_name}", fontsize=10)
                    ax.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    def create_data_loaders(self, validation_split=VALIDATION_SPLIT, test_split=0.0):
        """
        Create data loaders for training, validation, and optionally test
        
        Args:
            validation_split (float): Proportion for validation set
            test_split (float): Proportion for test set
        """
        print(f"\n Creating data loaders...")
        print(f"   Validation split: {validation_split:.1%}")
        if test_split > 0:
            print(f"   Test split: {test_split:.1%}")
        
        # Create data loaders
        data_info = create_data_loaders(
            data_path=self.data_path,
            batch_size=self.batch_size,
            validation_split=validation_split,
            test_split=test_split,
            num_workers=self.num_workers
        )
        
        # Store data loaders
        self.train_loader = data_info['train_loader']
        self.val_loader = data_info['val_loader']
        
        if 'test_loader' in data_info:
            self.test_loader = data_info['test_loader']
        
        # Update class information
        self.class_names = data_info['class_names']
        self.num_classes = data_info['num_classes']
        self.class_to_idx = data_info['class_to_idx']
        
        print(f"   Data loaders created successfully")
        print(f"   Training batches: {len(self.train_loader)}")
        print(f"   Validation batches: {len(self.val_loader)}")
    
    def build_model(self, model_type=MODEL_TYPE):
        """
        Build and configure the model
        
        Args:
            model_type (str): Type of model to build
            
        Returns:
            torch.nn.Module: Built model
        """
        print(f"\nBuilding model: {model_type}")
        print("-" * 40)
        
        if model_type.startswith('dinov2'):
            # Create DINOv2-based model
            self.model = create_dinov2_classifier(
                num_classes=self.num_classes,
                model_name=model_type,
                freeze_backbone=True
            )
        elif model_type == 'custom_cnn':
            # Create custom CNN
            self.model = create_herb_cnn(
                num_classes=self.num_classes,
                model_variant='standard'
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Move to device
        self.model = self.model.to(self.device)
        
        # Print model information
        model_info = self.get_model_summary()
        print(f"   Model built successfully")
        print(f"   Total parameters: {model_info['total_parameters']:,}")
        print(f"   Trainable parameters: {model_info['trainable_parameters']:,}")
        print(f"   Model size: {model_info['model_size_mb']:.2f} MB")
        
        return self.model
    
    def get_model_summary(self):
        """
        Get comprehensive model summary
        
        Returns:
            dict: Model information
        """
        if self.model is None:
            return {}
        
        if hasattr(self.model, 'get_model_info'):
            return self.model.get_model_info()
        else:
            # Fallback for models without get_model_info
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            
            return {
                'model_name': self.model.__class__.__name__,
                'total_parameters': total_params,
                'trainable_parameters': trainable_params,
                'model_size_mb': total_params * 4 / (1024 * 1024),
                'num_classes': self.num_classes
            }
    
    def train_model(self, epochs=EPOCHS, learning_rate=LEARNING_RATE, patience=PATIENCE):
        """
        Train the model with comprehensive monitoring
        
        Args:
            epochs (int): Number of training epochs
            learning_rate (float): Learning rate
            patience (int): Early stopping patience
            
        Returns:
            dict: Training history
        """
        print(f"\n  Starting training...")
        print(f"   Epochs: {epochs}")
        print(f"   Learning rate: {learning_rate}")
        print(f"   Patience: {patience}")
        print(f"   Device: {self.device}")
        
        # Training setup
        criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)
        optimizer = optim.AdamW(
            self.model.parameters(), 
            lr=learning_rate, 
            weight_decay=WEIGHT_DECAY
        )
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer, T_0=T_0, T_mult=T_MULT, eta_min=ETA_MIN
        )
        
        # Training state
        self.best_val_acc = 0.0
        patience_counter = 0
        self.training_start_time = time.time()
        
        # Training loop
        for epoch in range(epochs):
            print(f"\n Epoch {epoch+1}/{epochs}")
            print("-" * 50)
            
            # Training phase
            train_loss, train_acc = self._train_epoch(criterion, optimizer)
            
            # Validation phase
            val_loss, val_acc = self._validate_epoch(criterion)
            
            # Update scheduler
            scheduler.step()
            current_lr = optimizer.param_groups[0]['lr']
            
            # Save metrics
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            self.history['learning_rates'].append(current_lr)
            
            # Print epoch summary
            print(f"   Epoch {epoch+1} Summary:")
            print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
            print(f"   Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
            print(f"   Learning Rate: {current_lr:.6f}")
            
            # Early stopping and model checkpointing
            if val_acc > self.best_val_acc:
                self.best_val_acc = val_acc
                self.best_model_state = self.model.state_dict().copy()
                patience_counter = 0
                print(f"    New best validation accuracy: {self.best_val_acc:.4f}")
            else:
                patience_counter += 1
                print(f"    Patience: {patience_counter}/{patience}")
            
            if patience_counter >= patience:
                print(f"\n Early stopping triggered after {epoch+1} epochs")
                break
        
        # Load best model
        if self.best_model_state is not None:
            self.model.load_state_dict(self.best_model_state)
            print(f" Best model loaded with validation accuracy: {self.best_val_acc:.4f}")
        
        training_time = time.time() - self.training_start_time
        print(f"⏱  Total training time: {training_time/60:.1f} minutes")
        
        return self.history
    
    def _train_epoch(self, criterion, optimizer):
        """
        Train for one epoch
        
        Args:
            criterion: Loss function
            optimizer: Optimizer
            
        Returns:
            tuple: (average_loss, accuracy)
        """
        self.model.train()
        running_loss = 0.0
        correct_predictions = 0
        total_samples = 0
        
        train_pbar = tqdm(self.train_loader, desc="Training", leave=False)
        
        for batch_idx, (inputs, labels) in enumerate(train_pbar):
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), GRADIENT_CLIP_MAX_NORM)
            
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total_samples += labels.size(0)
            correct_predictions += (predicted == labels).sum().item()
            
            # Update progress bar
            current_loss = running_loss / (batch_idx + 1)
            current_acc = correct_predictions / total_samples
            train_pbar.set_postfix({
                'Loss': f'{current_loss:.4f}',
                'Acc': f'{current_acc:.4f}'
            })
        
        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = correct_predictions / total_samples
        
        return epoch_loss, epoch_acc
    
    def _validate_epoch(self, criterion):
        """
        Validate for one epoch
        
        Args:
            criterion: Loss function
            
        Returns:
            tuple: (average_loss, accuracy)
        """
        self.model.eval()
        running_loss = 0.0
        correct_predictions = 0
        total_samples = 0
        
        val_pbar = tqdm(self.val_loader, desc="Validation", leave=False)
        
        with torch.no_grad():
            for batch_idx, (inputs, labels) in enumerate(val_pbar):
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                
                # Statistics
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_samples += labels.size(0)
                correct_predictions += (predicted == labels).sum().item()
                
                # Update progress bar
                current_loss = running_loss / (batch_idx + 1)
                current_acc = correct_predictions / total_samples
                val_pbar.set_postfix({
                    'Loss': f'{current_loss:.4f}',
                    'Acc': f'{current_acc:.4f}'
                })
        
        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = correct_predictions / total_samples
        
        return epoch_loss, epoch_acc
    
    def plot_training_history(self):
        """
        Plot training history using evaluation module
        """
        if not self.history['train_loss']:
            print("  No training history available!")
            return
        
        print(f"\n Plotting training history...")
        plot_training_history(self.history)
    
    def evaluate_model(self):
        """
        Comprehensive model evaluation
        
        Returns:
            tuple: (accuracy, predictions, labels)
        """
        if self.model is None:
            print(" No model available for evaluation!")
            return None, None, None
        
        print(f"\n Evaluating model...")
        
        # Use evaluation module
        accuracy, predictions, labels = evaluate_model(
            self.model, 
            self.val_loader, 
            self.device, 
            self.class_names
        )
        
        return accuracy, predictions, labels
    
    def save_model_and_metadata(self, model_path=MODEL_SAVE_PATH):
        """
        Save model, metadata, and training history
        
        Args:
            model_path (str): Path to save the model
        """
        print(f"\n Saving model and metadata...")
        
        # Ensure save directory exists
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model checkpoint
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'model_info': self.get_model_summary(),
            'class_names': self.class_names,
            'num_classes': self.num_classes,
            'class_to_idx': self.class_to_idx,
            'img_size': self.img_size,
            'best_val_acc': self.best_val_acc,
            'training_history': self.history
        }
        
        torch.save(checkpoint, model_path)
        print(f"    Model saved: {model_path}")
        
        # Save metadata JSON
        metadata = {
            'model_info': self.get_model_summary(),
            'class_names': self.class_names,
            'num_classes': self.num_classes,
            'class_to_idx': self.class_to_idx,
            'img_size': self.img_size,
            'best_val_acc': self.best_val_acc,
            'model_path': model_path,
            'training_config': {
                'batch_size': self.batch_size,
                'img_size': self.img_size,
                'device': str(self.device)
            }
        }
        
        metadata_path = METADATA_PATH
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"    Metadata saved: {metadata_path}")
        
        # Save training history
        if self.history['train_loss']:
            history_path = HISTORY_PATH
            with open(history_path, 'wb') as f:
                pickle.dump(self.history, f)
            print(f"    Training history saved: {history_path}")
    
    def load_model_and_metadata(self, model_path=MODEL_SAVE_PATH):
        """
        Load model and metadata from checkpoint
        
        Args:
            model_path (str): Path to the saved model
        """
        print(f"\n Loading model from {model_path}...")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Extract metadata
        self.class_names = checkpoint['class_names']
        self.num_classes = checkpoint['num_classes']
        self.class_to_idx = checkpoint.get('class_to_idx', {})
        self.img_size = checkpoint.get('img_size', IMG_SIZE)
        self.best_val_acc = checkpoint.get('best_val_acc', 0.0)
        
        # Load training history if available
        if 'training_history' in checkpoint:
            self.history = checkpoint['training_history']
        
        # Build model architecture (need to know model type)
        model_info = checkpoint.get('model_info', {})
        model_name = model_info.get('model_name', 'unknown')
        
        if 'dinov2' in model_name.lower():
            # Assume DINOv2 model - would need more info to determine exact variant
            self.model = create_dinov2_classifier(self.num_classes, 'dinov2_vitl14')
        else:
            # Assume custom CNN
            self.model = create_herb_cnn(self.num_classes, 'standard')
        
        # Load model weights
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        
        print(f"   Model loaded successfully")
        print(f"   Classes: {len(self.class_names)}")
        print(f"   Best validation accuracy: {self.best_val_acc:.4f}")
        
        return self.model