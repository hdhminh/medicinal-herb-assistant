"""
data/dataset.py - HerbDataset Implementation

This module contains:
- Custom Dataset class for herb images with robust loading
- AVIF format handling and error recovery
- Placeholder generation for failed image loads
- Dataset validation and statistics
- Memory-efficient image loading
"""

import os
import warnings
import torch
from torch.utils.data import Dataset
from PIL import Image
from utils.image_utils import load_image_robust, create_placeholder_image
from config import SUPPORTED_EXTENSIONS

# Suppress AVIF-related warnings
warnings.filterwarnings("ignore", message="image file could not be identified because AVIF support not installed")

class HerbDataset(Dataset):
    """
    Custom Dataset class for herb images with enhanced error handling
    
    Features:
    - Robust image loading supporting multiple formats including AVIF
    - Automatic placeholder generation for corrupted/unreadable images
    - Comprehensive error tracking and reporting
    - Memory-efficient loading with on-demand processing
    - Support for both training and validation modes
    
    Args:
        data_path (str): Path to the dataset root directory
        transform (callable, optional): Optional transform to be applied on images
        split (str): Dataset split identifier ('train', 'val', 'test')
        max_failures (int): Maximum number of failed loads to track
        verbose (bool): Whether to print loading information
    """
    
    def __init__(self, data_path, transform=None, split='train', max_failures=50, verbose=True):
        self.data_path = data_path
        self.transform = transform
        self.split = split
        self.max_failures = max_failures
        self.verbose = verbose
        
        # Initialize tracking variables
        self.failed_loads = []
        self.success_count = 0
        self.failure_count = 0
        
        # Validate data path
        if not os.path.exists(data_path):
            raise ValueError(f"Data path does not exist: {data_path}")
        
        # Get all classes (subdirectories)
        self.classes = sorted([d for d in os.listdir(data_path) 
                              if os.path.isdir(os.path.join(data_path, d))])
        
        if not self.classes:
            raise ValueError(f"No class directories found in {data_path}")
        
        # Create class to index mapping
        self.class_to_idx = {cls_name: idx for idx, cls_name in enumerate(self.classes)}
        self.idx_to_class = {idx: cls_name for cls_name, idx in self.class_to_idx.items()}
        
        # Collect all image samples
        self.samples = []
        self._collect_samples()
        
        if verbose:
            print(f"   Dataset initialized: {split}")
            print(f"   Path: {data_path}")
            print(f"   Classes: {len(self.classes)}")
            print(f"   Total samples: {len(self.samples)}")
            print(f"   Class names: {self.classes}")
    
    def _collect_samples(self):
        """
        Collect all image file paths and their corresponding labels
        """
        for class_name in self.classes:
            class_path = os.path.join(self.data_path, class_name)
            class_idx = self.class_to_idx[class_name]
            
            # Walk through class directory (including subdirectories)
            for root, dirs, files in os.walk(class_path):
                for img_file in files:
                    if img_file.lower().endswith(SUPPORTED_EXTENSIONS):
                        img_path = os.path.join(root, img_file)
                        if os.path.isfile(img_path):
                            self.samples.append((img_path, class_idx))
        
        if len(self.samples) == 0:
            raise ValueError(f"No valid image files found in {self.data_path}")
    
    def __len__(self):
        """Return the total number of samples"""
        return len(self.samples)
    
    def __getitem__(self, idx):
        """
        Get a sample from the dataset
        
        Args:
            idx (int): Sample index
            
        Returns:
            tuple: (image, label) where image is PIL Image or Tensor and label is int
        """
        img_path, label = self.samples[idx]
        
        # Try to load image using robust loading
        image = load_image_robust(img_path)
        
        if image is None:
            # Track failed loads (up to max_failures to avoid memory issues)
            if len(self.failed_loads) < self.max_failures:
                self.failed_loads.append({
                    'path': img_path,
                    'index': idx,
                    'class': self.idx_to_class[label]
                })
            
            self.failure_count += 1
            
            # Print first few failures for debugging
            if self.failure_count <= 5 and self.verbose:
                print(f"  Failed to load: {os.path.basename(img_path)} (class: {self.idx_to_class[label]})")
            
            # Create placeholder image with class-specific pattern
            image = create_placeholder_image(label, (392, 392))
        else:
            self.success_count += 1
        
        # Apply transforms if provided
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def get_class_distribution(self):
        """
        Get the distribution of classes in the dataset
        
        Returns:
            dict: Class name to count mapping
        """
        class_counts = {}
        for _, label in self.samples:
            class_name = self.idx_to_class[label]
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        return class_counts
    
    def get_failure_report(self):
        """
        Get detailed report of loading failures
        
        Returns:
            dict: Failure statistics and details
        """
        failure_by_class = {}
        for failure in self.failed_loads:
            class_name = failure['class']
            if class_name not in failure_by_class:
                failure_by_class[class_name] = []
            failure_by_class[class_name].append(failure)
        
        return {
            'total_attempts': self.success_count + self.failure_count,
            'successful_loads': self.success_count,
            'failed_loads': self.failure_count,
            'failure_rate': self.failure_count / (self.success_count + self.failure_count) if (self.success_count + self.failure_count) > 0 else 0,
            'failures_by_class': failure_by_class,
            'sample_failures': self.failed_loads[:10]  # First 10 failures for inspection
        }
    
    def print_dataset_stats(self):
        """Print comprehensive dataset statistics"""
        print("="*60)
        print(f"DATASET STATISTICS - {self.split.upper()}")
        print("="*60)
        
        # Basic stats
        print(f"Total samples: {len(self.samples)}")
        print(f"Number of classes: {len(self.classes)}")
        
        # Class distribution
        class_dist = self.get_class_distribution()
        print(f"\nClass distribution:")
        for class_name, count in sorted(class_dist.items()):
            percentage = (count / len(self.samples)) * 100
            print(f"  {class_name}: {count} ({percentage:.1f}%)")
        
        # Loading statistics (if any loads have been attempted)
        if self.success_count > 0 or self.failure_count > 0:
            failure_report = self.get_failure_report()
            print(f"\nLoading statistics:")
            print(f"  Successful loads: {failure_report['successful_loads']}")
            print(f"  Failed loads: {failure_report['failed_loads']}")
            print(f"  Failure rate: {failure_report['failure_rate']:.2%}")
            
            if failure_report['failures_by_class']:
                print(f"  Classes with failures:")
                for class_name, failures in failure_report['failures_by_class'].items():
                    print(f"    {class_name}: {len(failures)} failures")
        
        print("="*60)
    
    def validate_dataset(self, sample_size=100):
        """
        Validate a sample of the dataset by attempting to load images
        
        Args:
            sample_size (int): Number of random samples to validate
            
        Returns:
            dict: Validation results
        """
        import random
        
        if sample_size > len(self.samples):
            sample_size = len(self.samples)
        
        # Random sample of indices
        sample_indices = random.sample(range(len(self.samples)), sample_size)
        
        validation_results = {
            'total_tested': sample_size,
            'successful': 0,
            'failed': 0,
            'corrupted_files': [],
            'missing_files': []
        }
        
        print(f" Validating {sample_size} random samples...")
        
        for idx in sample_indices:
            img_path, label = self.samples[idx]
            
            # Check if file exists
            if not os.path.exists(img_path):
                validation_results['missing_files'].append(img_path)
                validation_results['failed'] += 1
                continue
            
            # Try to load image
            image = load_image_robust(img_path)
            if image is None:
                validation_results['corrupted_files'].append(img_path)
                validation_results['failed'] += 1
            else:
                validation_results['successful'] += 1
        
        success_rate = validation_results['successful'] / sample_size
        print(f" Validation complete: {success_rate:.1%} success rate")
        
        if validation_results['missing_files']:
            print(f"  Missing files: {len(validation_results['missing_files'])}")
        
        if validation_results['corrupted_files']:
            print(f"  Corrupted files: {len(validation_results['corrupted_files'])}")
        
        return validation_results
    
    def get_sample_for_class(self, class_name, count=1):
        """
        Get sample images from a specific class
        
        Args:
            class_name (str): Name of the class
            count (int): Number of samples to return
            
        Returns:
            list: List of (image, label) tuples
        """
        if class_name not in self.class_to_idx:
            raise ValueError(f"Class '{class_name}' not found in dataset")
        
        class_idx = self.class_to_idx[class_name]
        class_samples = [(path, label) for path, label in self.samples if label == class_idx]
        
        if count > len(class_samples):
            count = len(class_samples)
        
        import random
        selected_samples = random.sample(class_samples, count)
        
        results = []
        for img_path, label in selected_samples:
            image = load_image_robust(img_path)
            if image is None:
                image = create_placeholder_image(label)
            results.append((image, label))
        
        return results


class MemoryEfficientHerbDataset(HerbDataset):
    """
    Memory-efficient version of HerbDataset that loads images on-demand
    and implements caching for frequently accessed images
    
    Args:
        cache_size (int): Maximum number of images to keep in memory cache
        **kwargs: Arguments passed to parent HerbDataset
    """
    
    def __init__(self, cache_size=1000, **kwargs):
        super().__init__(**kwargs)
        
        self.cache_size = cache_size
        self.image_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.access_count = {}
        
        print(f" Memory-efficient dataset with cache size: {cache_size}")
    
    def __getitem__(self, idx):
        """
        Get item with caching support
        """
        img_path, label = self.samples[idx]
        
        # Check cache first
        if img_path in self.image_cache:
            image = self.image_cache[img_path]
            self.cache_hits += 1
        else:
            # Load image
            image = load_image_robust(img_path)
            self.cache_misses += 1
            
            if image is None:
                # Track failure and create placeholder
                if len(self.failed_loads) < self.max_failures:
                    self.failed_loads.append({
                        'path': img_path,
                        'index': idx,
                        'class': self.idx_to_class[label]
                    })
                self.failure_count += 1
                image = create_placeholder_image(label, (392, 392))
            else:
                self.success_count += 1
                
                # Add to cache if there's space
                if len(self.image_cache) < self.cache_size:
                    self.image_cache[img_path] = image
                elif len(self.image_cache) >= self.cache_size:
                    # Remove least accessed item
                    least_accessed = min(self.access_count, key=self.access_count.get)
                    del self.image_cache[least_accessed]
                    del self.access_count[least_accessed]
                    self.image_cache[img_path] = image
        
        # Track access for cache management
        self.access_count[img_path] = self.access_count.get(img_path, 0) + 1
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        return image, label
    
    def get_cache_stats(self):
        """
        Get cache performance statistics
        
        Returns:
            dict: Cache statistics
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.image_cache),
            'max_cache_size': self.cache_size,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def clear_cache(self):
        """Clear the image cache"""
        self.image_cache.clear()
        self.access_count.clear()
        print("  Image cache cleared")


def create_herb_dataset(data_path, transform=None, split='train', 
                       memory_efficient=False, **kwargs):
    """
    Factory function to create HerbDataset instances
    
    Args:
        data_path (str): Path to dataset
        transform (callable): Image transforms
        split (str): Dataset split name
        memory_efficient (bool): Whether to use memory-efficient version
        **kwargs: Additional arguments
        
    Returns:
        HerbDataset: Dataset instance
    """
    if memory_efficient:
        return MemoryEfficientHerbDataset(
            data_path=data_path,
            transform=transform,
            split=split,
            **kwargs
        )
    else:
        return HerbDataset(
            data_path=data_path,
            transform=transform,
            split=split,
            **kwargs
        )