"""
utils/data_utils.py - Data Processing Utility Functions

This module handles:
- Dataset structure analysis
- Class distribution calculations
- Data splitting utilities
- File organization helpers
- Dataset validation functions
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from config import SUPPORTED_EXTENSIONS, FIGURE_SIZE_DISTRIBUTION

def analyze_dataset_structure(data_path, verbose=True):
    """
    Analyze the structure and distribution of the dataset
    
    Args:
        data_path (str): Path to dataset root directory
        verbose (bool): Whether to print detailed analysis
        
    Returns:
        dict: Dataset structure analysis
    """
    analysis = {
        'total_classes': 0,
        'total_images': 0,
        'class_names': [],
        'class_counts': {},
        'min_images_per_class': float('inf'),
        'max_images_per_class': 0,
        'mean_images_per_class': 0,
        'std_images_per_class': 0,
        'is_balanced': False,
        'balance_ratio': 0
    }
    
    # Get all subdirectories (classes)
    class_names = [d for d in os.listdir(data_path) 
                   if os.path.isdir(os.path.join(data_path, d))]
    class_names.sort()
    
    analysis['class_names'] = class_names
    analysis['total_classes'] = len(class_names)
    
    # Count images per class
    class_counts = {}
    for class_name in class_names:
        class_path = os.path.join(data_path, class_name)
        image_files = [f for f in os.listdir(class_path) 
                      if f.lower().endswith(SUPPORTED_EXTENSIONS)]
        class_counts[class_name] = len(image_files)
        analysis['total_images'] += len(image_files)
    
    analysis['class_counts'] = class_counts
    
    # Calculate statistics
    if class_counts:
        counts = list(class_counts.values())
        analysis['min_images_per_class'] = min(counts)
        analysis['max_images_per_class'] = max(counts)
        analysis['mean_images_per_class'] = np.mean(counts)
        analysis['std_images_per_class'] = np.std(counts)
        
        # Check if dataset is balanced (using coefficient of variation)
        cv = analysis['std_images_per_class'] / analysis['mean_images_per_class'] if analysis['mean_images_per_class'] > 0 else 0
        analysis['is_balanced'] = cv < 0.2  # Less than 20% variation
        analysis['balance_ratio'] = analysis['min_images_per_class'] / analysis['max_images_per_class'] if analysis['max_images_per_class'] > 0 else 0
    
    if verbose:
        print("="*60)
        print("DATASET STRUCTURE ANALYSIS")
        print("="*60)
        print(f"Total Classes: {analysis['total_classes']}")
        print(f"Total Images: {analysis['total_images']}")
        print(f"Images per Class - Min: {analysis['min_images_per_class']}, Max: {analysis['max_images_per_class']}")
        print(f"Images per Class - Mean: {analysis['mean_images_per_class']:.1f}, Std: {analysis['std_images_per_class']:.1f}")
        print(f"Dataset Balance: {'Balanced' if analysis['is_balanced'] else 'Imbalanced'} (ratio: {analysis['balance_ratio']:.2f})")
        
        print(f"\nClass Distribution:")
        for class_name, count in class_counts.items():
            percentage = (count / analysis['total_images']) * 100
            print(f"  {class_name}: {count} images ({percentage:.1f}%)")
        print("="*60)
    
    return analysis

def visualize_class_distribution(class_counts, save_path=None):
    """
    Create visualization of class distribution
    
    Args:
        class_counts (dict): Dictionary mapping class names to image counts
        save_path (str, optional): Path to save the plot
        
    Returns:
        matplotlib.figure.Figure: The created figure
    """
    plt.figure(figsize=FIGURE_SIZE_DISTRIBUTION)
    
    classes = list(class_counts.keys())
    counts = list(class_counts.values())
    
    # Create bar plot
    bars = plt.bar(classes, counts, color='skyblue', alpha=0.7, edgecolor='navy')
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Distribution of Images per Herb Class', fontsize=16, fontweight='bold')
    plt.xlabel('Herb Classes', fontsize=12)
    plt.ylabel('Number of Images', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add statistics text
    total_images = sum(counts)
    mean_count = np.mean(counts)
    std_count = np.std(counts)
    
    stats_text = f'Total: {total_images} images\nMean: {mean_count:.1f} ± {std_count:.1f}'
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Distribution plot saved to: {save_path}")
    
    plt.show()
    
    return plt.gcf()

def calculate_split_indices(dataset_size, validation_split=0.2, test_split=0.1, random_seed=42):
    """
    Calculate indices for train/validation/test splits
    
    Args:
        dataset_size (int): Total number of samples
        validation_split (float): Proportion for validation set
        test_split (float): Proportion for test set
        random_seed (int): Random seed for reproducibility
        
    Returns:
        tuple: (train_indices, val_indices, test_indices)
    """
    indices = list(range(dataset_size))
    np.random.seed(random_seed)
    np.random.shuffle(indices)
    
    # Calculate split sizes
    test_size = int(test_split * dataset_size)
    val_size = int(validation_split * dataset_size)
    train_size = dataset_size - val_size - test_size
    
    # Split indices
    test_indices = indices[:test_size] if test_size > 0 else []
    val_indices = indices[test_size:test_size + val_size]
    train_indices = indices[test_size + val_size:]
    
    return train_indices, val_indices, test_indices

def create_stratified_split(class_labels, validation_split=0.2, test_split=0.1, random_seed=42):
    """
    Create stratified split maintaining class proportions
    
    Args:
        class_labels (list): List of class labels for each sample
        validation_split (float): Proportion for validation set
        test_split (float): Proportion for test set
        random_seed (int): Random seed for reproducibility
        
    Returns:
        tuple: (train_indices, val_indices, test_indices)
    """
    np.random.seed(random_seed)
    
    # Group indices by class
    class_indices = {}
    for idx, label in enumerate(class_labels):
        if label not in class_indices:
            class_indices[label] = []
        class_indices[label].append(idx)
    
    train_indices = []
    val_indices = []
    test_indices = []
    
    # Split each class separately
    for label, indices in class_indices.items():
        np.random.shuffle(indices)
        
        class_size = len(indices)
        test_size = int(test_split * class_size)
        val_size = int(validation_split * class_size)
        
        test_indices.extend(indices[:test_size])
        val_indices.extend(indices[test_size:test_size + val_size])
        train_indices.extend(indices[test_size + val_size:])
    
    # Shuffle the final splits
    np.random.shuffle(train_indices)
    np.random.shuffle(val_indices)
    np.random.shuffle(test_indices)
    
    return train_indices, val_indices, test_indices

def validate_data_split(train_indices, val_indices, test_indices, class_labels, verbose=True):
    """
    Validate that data split maintains reasonable class distribution
    
    Args:
        train_indices (list): Training set indices
        val_indices (list): Validation set indices  
        test_indices (list): Test set indices
        class_labels (list): Complete list of class labels
        verbose (bool): Whether to print validation results
        
    Returns:
        dict: Validation results
    """
    def get_class_distribution(indices, labels):
        subset_labels = [labels[i] for i in indices]
        return Counter(subset_labels)
    
    train_dist = get_class_distribution(train_indices, class_labels)
    val_dist = get_class_distribution(val_indices, class_labels)
    test_dist = get_class_distribution(test_indices, class_labels) if test_indices else {}
    
    total_samples = len(class_labels)
    unique_classes = set(class_labels)
    
    validation_results = {
        'total_samples': total_samples,
        'train_samples': len(train_indices),
        'val_samples': len(val_indices),
        'test_samples': len(test_indices),
        'train_ratio': len(train_indices) / total_samples,
        'val_ratio': len(val_indices) / total_samples,
        'test_ratio': len(test_indices) / total_samples if test_indices else 0,
        'classes_in_train': len(train_dist),
        'classes_in_val': len(val_dist),
        'classes_in_test': len(test_dist),
        'all_classes_represented': len(train_dist) == len(unique_classes) and len(val_dist) == len(unique_classes)
    }
    
    if verbose:
        print("="*50)
        print("DATA SPLIT VALIDATION")
        print("="*50)
        print(f"Total Samples: {total_samples}")
        print(f"Train: {len(train_indices)} ({validation_results['train_ratio']:.1%})")
        print(f"Validation: {len(val_indices)} ({validation_results['val_ratio']:.1%})")
        if test_indices:
            print(f"Test: {len(test_indices)} ({validation_results['test_ratio']:.1%})")
        
        print(f"\nClass Representation:")
        print(f"Unique Classes: {len(unique_classes)}")
        print(f"Classes in Train: {validation_results['classes_in_train']}")
        print(f"Classes in Validation: {validation_results['classes_in_val']}")
        if test_indices:
            print(f"Classes in Test: {validation_results['classes_in_test']}")
        
        print(f"All Classes Represented: {validation_results['all_classes_represented']}")
        print("="*50)
    
    return validation_results

def get_class_weights(class_counts, method='inverse_frequency'):
    """
    Calculate class weights for handling imbalanced datasets
    
    Args:
        class_counts (dict): Dictionary mapping class names to counts
        method (str): Method to calculate weights ('inverse_frequency', 'balanced')
        
    Returns:
        dict: Dictionary mapping class names to weights
    """
    total_samples = sum(class_counts.values())
    num_classes = len(class_counts)
    
    if method == 'inverse_frequency':
        # Weight inversely proportional to class frequency
        weights = {class_name: total_samples / (num_classes * count) 
                  for class_name, count in class_counts.items()}
    
    elif method == 'balanced':
        # Standard balanced class weights
        weights = {class_name: total_samples / (num_classes * count) 
                  for class_name, count in class_counts.items()}
    
    else:
        raise ValueError(f"Unknown weighting method: {method}")
    
    return weights

def print_dataset_summary(data_path):
    """
    Print comprehensive dataset summary
    
    Args:
        data_path (str): Path to dataset root directory
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE DATASET SUMMARY")
    print("="*70)
    
    # Basic structure analysis
    structure = analyze_dataset_structure(data_path, verbose=False)
    
    print(f"Dataset Path: {data_path}")
    print(f"Total Classes: {structure['total_classes']}")
    print(f"Total Images: {structure['total_images']}")
    print(f"Average Images per Class: {structure['mean_images_per_class']:.1f}")
    
    # Balance analysis
    balance_status = "Balanced" if structure['is_balanced'] else "⚠️ Imbalanced"
    print(f"Dataset Balance: {balance_status} (ratio: {structure['balance_ratio']:.2f})")
    
    # Recommendations
    print(f"\nRecommendations:")
    if not structure['is_balanced']:
        print("  • Consider data augmentation for underrepresented classes")
        print("  • Use class weights during training")
    
    if structure['min_images_per_class'] < 50:
        print("  • Some classes have very few samples - consider collecting more data")
    
    if structure['total_images'] < 1000:
        print("  • Small dataset - consider transfer learning and heavy augmentation")
    
    print("="*70 + "\n")
    
    return structure