"""
data/data_loader.py - Data Loading and Transform Utilities

This module handles:
- Transform definitions for training and validation
- DataLoader creation with proper parameters
- Data augmentation configurations
- Memory-efficient loading strategies
"""

import torch
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
import numpy as np

from .dataset import create_herb_dataset
from config import (
    IMG_SIZE, NORMALIZE_MEAN, NORMALIZE_STD,
    ROTATION_DEGREES, HORIZONTAL_FLIP_PROB, VERTICAL_FLIP_PROB,
    BRIGHTNESS_FACTOR, CONTRAST_FACTOR, SATURATION_FACTOR, HUE_FACTOR,
    TRANSLATE_FACTOR, SCALE_FACTOR,
    NUM_WORKERS, PIN_MEMORY, SHUFFLE_TRAIN, SHUFFLE_VAL,
    RANDOM_SEED
)

def get_transforms(augment=True, image_size=IMG_SIZE):
    """
    Get image transforms for training and validation
    
    Args:
        augment (bool): Whether to apply augmentation (for training)
        image_size (tuple): Target image size (height, width)
        
    Returns:
        torchvision.transforms.Compose: Transform pipeline
    """
    
    if augment:
        # Training transforms with aggressive augmentation
        transform = transforms.Compose([
            # Resize and crop
            transforms.Resize((int(image_size[0] * 1.1), int(image_size[1] * 1.1))),
            transforms.CenterCrop(image_size),
            
            # Geometric augmentations
            transforms.RandomRotation(
                degrees=ROTATION_DEGREES,
                interpolation=transforms.InterpolationMode.BILINEAR,
                fill=0
            ),
            transforms.RandomHorizontalFlip(p=HORIZONTAL_FLIP_PROB),
            transforms.RandomVerticalFlip(p=VERTICAL_FLIP_PROB),
            
            # Affine transformations
            transforms.RandomAffine(
                degrees=0,
                translate=TRANSLATE_FACTOR,
                scale=SCALE_FACTOR,
                interpolation=transforms.InterpolationMode.BILINEAR,
                fill=0
            ),
            
            # Color augmentations
            transforms.ColorJitter(
                brightness=BRIGHTNESS_FACTOR,
                contrast=CONTRAST_FACTOR,
                saturation=SATURATION_FACTOR,
                hue=HUE_FACTOR
            ),
            
            # Additional augmentations for better generalization
            transforms.RandomGrayscale(p=0.1),
            transforms.RandomPerspective(distortion_scale=0.1, p=0.3),
            
            # Convert to tensor and normalize
            transforms.ToTensor(),
            transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD),
            
            # Random erasing for robustness
            transforms.RandomErasing(p=0.1, scale=(0.02, 0.1), ratio=(0.3, 3.3))
        ])
        
    else:
        # Validation/test transforms - no augmentation
        transform = transforms.Compose([
            transforms.Resize((int(image_size[0] * 1.05), int(image_size[1] * 1.05))),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD)
        ])
    
    return transform

def get_inference_transforms(image_size=IMG_SIZE):
    """
    Get transforms specifically for inference/prediction
    
    Args:
        image_size (tuple): Target image size
        
    Returns:
        torchvision.transforms.Compose: Inference transform pipeline
    """
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD)
    ])

def create_data_splits(dataset, validation_split=0.3, test_split=0.0, stratify=True):
    """
    Create train/validation/test splits from a dataset
    
    Args:
        dataset: Dataset to split
        validation_split (float): Proportion for validation
        test_split (float): Proportion for test (0 = no test set)
        stratify (bool): Whether to maintain class proportions
        
    Returns:
        tuple: (train_indices, val_indices, test_indices)
    """
    dataset_size = len(dataset)
    
    if stratify and hasattr(dataset, 'samples'):
        # Stratified split maintaining class proportions
        from utils.data_utils import create_stratified_split
        
        # Extract labels from samples
        labels = [label for _, label in dataset.samples]
        train_indices, val_indices, test_indices = create_stratified_split(
            labels, validation_split, test_split, RANDOM_SEED
        )
    else:
        # Random split
        indices = list(range(dataset_size))
        np.random.seed(RANDOM_SEED)
        np.random.shuffle(indices)
        
        # Calculate split sizes
        test_size = int(test_split * dataset_size) if test_split > 0 else 0
        val_size = int(validation_split * dataset_size)
        train_size = dataset_size - val_size - test_size
        
        # Create splits
        test_indices = indices[:test_size] if test_size > 0 else []
        val_indices = indices[test_size:test_size + val_size]
        train_indices = indices[test_size + val_size:]
    
    return train_indices, val_indices, test_indices

def create_data_loaders(data_path, batch_size=16, validation_split=0.3, 
                       test_split=0.0, num_workers=NUM_WORKERS,
                       memory_efficient=False, stratify=True, **kwargs):
    """
    Create train, validation, and optionally test data loaders
    
    Args:
        data_path (str): Path to dataset directory
        batch_size (int): Batch size for data loaders
        validation_split (float): Proportion of data for validation
        test_split (float): Proportion of data for test (0 = no test set)
        num_workers (int): Number of worker processes for data loading
        memory_efficient (bool): Whether to use memory-efficient dataset
        stratify (bool): Whether to maintain class proportions in splits
        **kwargs: Additional arguments for dataset creation
        
    Returns:
        dict: Dictionary containing data loaders and dataset info
    """
    
    print(f"   Creating data loaders...")
    print(f"   Batch size: {batch_size}")
    print(f"   Validation split: {validation_split:.1%}")
    if test_split > 0:
        print(f"   Test split: {test_split:.1%}")
    print(f"   Stratified: {stratify}")
    print(f"   Memory efficient: {memory_efficient}")
    
    # Create transforms
    train_transform = get_transforms(augment=True)
    val_transform = get_transforms(augment=False)
    
    # Create datasets
    train_dataset = create_herb_dataset(
        data_path=data_path,
        transform=train_transform,
        split='train',
        memory_efficient=memory_efficient,
        **kwargs
    )
    
    val_dataset = create_herb_dataset(
        data_path=data_path,
        transform=val_transform,
        split='validation',
        memory_efficient=memory_efficient,
        **kwargs
    )
    
    # Create data splits
    train_indices, val_indices, test_indices = create_data_splits(
        train_dataset, validation_split, test_split, stratify
    )
    
    # Create subset datasets
    train_subset = Subset(train_dataset, train_indices)
    val_subset = Subset(val_dataset, val_indices)
    
    # Determine optimal number of workers based on system
    if num_workers == -1:
        import os
        num_workers = min(8, os.cpu_count() or 1)
    
    # Create data loaders
    train_loader = DataLoader(
        train_subset,
        batch_size=batch_size,
        shuffle=SHUFFLE_TRAIN,
        num_workers=num_workers,
        pin_memory=PIN_MEMORY and torch.cuda.is_available(),
        drop_last=True,  # Drop last incomplete batch for training stability
        persistent_workers=num_workers > 0
    )
    
    val_loader = DataLoader(
        val_subset,
        batch_size=batch_size,
        shuffle=SHUFFLE_VAL,
        num_workers=num_workers,
        pin_memory=PIN_MEMORY and torch.cuda.is_available(),
        drop_last=False,
        persistent_workers=num_workers > 0
    )
    
    result = {
        'train_loader': train_loader,
        'val_loader': val_loader,
        'train_dataset': train_dataset,
        'val_dataset': val_dataset,
        'class_names': train_dataset.classes,
        'num_classes': len(train_dataset.classes),
        'train_size': len(train_indices),
        'val_size': len(val_indices),
        'class_to_idx': train_dataset.class_to_idx
    }
    
    # Add test loader if requested
    if test_split > 0 and len(test_indices) > 0:
        test_dataset = create_herb_dataset(
            data_path=data_path,
            transform=val_transform,
            split='test',
            memory_efficient=memory_efficient,
            **kwargs
        )
        test_subset = Subset(test_dataset, test_indices)
        
        test_loader = DataLoader(
            test_subset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=PIN_MEMORY and torch.cuda.is_available(),
            drop_last=False,
            persistent_workers=num_workers > 0
        )
        
        result['test_loader'] = test_loader
        result['test_dataset'] = test_dataset
        result['test_size'] = len(test_indices)
    
    # Print summary
    print(f"   Data loaders created:")
    print(f"   Training samples: {result['train_size']}")
    print(f"   Validation samples: {result['val_size']}")
    if 'test_size' in result:
        print(f"   Test samples: {result['test_size']}")
    print(f"   Classes: {result['num_classes']}")
    print(f"   Class names: {result['class_names']}")
    
    return result

def get_class_weights(class_counts, method='balanced'):
    """
    Calculate class weights for handling imbalanced datasets
    
    Args:
        class_counts (dict): Dictionary mapping class names to counts
        method (str): Weighting method ('balanced', 'inverse_freq')
        
    Returns:
        torch.Tensor: Class weights tensor
    """
    total_samples = sum(class_counts.values())
    num_classes = len(class_counts)
    
    if method == 'balanced':
        # Balanced class weights
        weights = []
        for class_name in sorted(class_counts.keys()):
            count = class_counts[class_name]
            weight = total_samples / (num_classes * count)
            weights.append(weight)
    
    elif method == 'inverse_freq':
        # Inverse frequency weights
        weights = []
        for class_name in sorted(class_counts.keys()):
            count = class_counts[class_name]
            weight = 1.0 / count
            weights.append(weight)
    
    else:
        raise ValueError(f"Unknown weighting method: {method}")
    
    return torch.FloatTensor(weights)

def create_weighted_sampler(dataset, class_weights=None):
    """
    Create a weighted random sampler for handling imbalanced datasets
    
    Args:
        dataset: Dataset with samples attribute
        class_weights (torch.Tensor, optional): Pre-computed class weights
        
    Returns:
        torch.utils.data.WeightedRandomSampler: Weighted sampler
    """
    from torch.utils.data import WeightedRandomSampler
    
    # Get class distribution
    if hasattr(dataset, 'get_class_distribution'):
        class_counts = dataset.get_class_distribution()
    else:
        # Fallback: count from samples
        class_counts = {}
        for _, label in dataset.samples:
            class_name = dataset.idx_to_class.get(label, str(label))
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    # Calculate weights if not provided
    if class_weights is None:
        class_weights = get_class_weights(class_counts, method='balanced')
    
    # Create sample weights
    sample_weights = []
    for _, label in dataset.samples:
        sample_weights.append(class_weights[label])
    
    # Create sampler
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )
    
    return sampler

def visualize_batch(data_loader, num_samples=8, denormalize=True):
    """
    Visualize a batch of images from the data loader
    
    Args:
        data_loader: DataLoader to sample from
        num_samples (int): Number of images to display
        denormalize (bool): Whether to denormalize images for display
    """
    import matplotlib.pyplot as plt
    from torchvision.utils import make_grid
    
    # Get a batch
    data_iter = iter(data_loader)
    images, labels = next(data_iter)
    
    # Select subset
    images = images[:num_samples]
    labels = labels[:num_samples]
    
    # Denormalize if requested
    if denormalize:
        mean = torch.tensor(NORMALIZE_MEAN).view(3, 1, 1)
        std = torch.tensor(NORMALIZE_STD).view(3, 1, 1)
        images = images * std + mean
        images = torch.clamp(images, 0, 1)
    
    # Create grid
    grid = make_grid(images, nrow=4, padding=2, normalize=False)
    
    # Plot
    plt.figure(figsize=(12, 8))
    plt.imshow(grid.permute(1, 2, 0))
    plt.axis('off')
    plt.title(f'Sample Batch from Data Loader\nLabels: {labels.tolist()}')
    plt.tight_layout()
    plt.show()

def print_data_loader_info(data_loaders_dict):
    """
    Print comprehensive information about data loaders
    
    Args:
        data_loaders_dict (dict): Dictionary containing data loaders and info
    """
    print("="*60)
    print("DATA LOADER INFORMATION")
    print("="*60)
    
    # Basic info
    print(f"Number of classes: {data_loaders_dict['num_classes']}")
    print(f"Class names: {data_loaders_dict['class_names']}")
    
    # Dataset sizes
    print(f"\nDataset sizes:")
    print(f"  Training: {data_loaders_dict['train_size']}")
    print(f"  Validation: {data_loaders_dict['val_size']}")
    if 'test_size' in data_loaders_dict:
        print(f"  Test: {data_loaders_dict['test_size']}")
    
    # Loader info
    train_loader = data_loaders_dict['train_loader']
    print(f"\nData loader configuration:")
    print(f"  Batch size: {train_loader.batch_size}")
    print(f"  Number of workers: {train_loader.num_workers}")
    print(f"  Pin memory: {train_loader.pin_memory}")
    print(f"  Training batches: {len(train_loader)}")
    print(f"  Validation batches: {len(data_loaders_dict['val_loader'])}")
    
    # Class distribution
    train_dataset = data_loaders_dict['train_dataset']
    if hasattr(train_dataset, 'get_class_distribution'):
        class_dist = train_dataset.get_class_distribution()
        print(f"\nClass distribution:")
        total = sum(class_dist.values())
        for class_name, count in sorted(class_dist.items()):
            percentage = (count / total) * 100
            print(f"  {class_name}: {count} ({percentage:.1f}%)")
    
    print("="*60)