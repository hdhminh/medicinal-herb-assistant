"""
utils/gpu_setup.py - GPU Configuration and Device Management

This module handles:
- GPU detection and configuration
- CUDA optimization settings
- Device selection and setup
- Memory management
- Performance optimization flags
"""

import torch
import numpy as np
from config import (
    CUDA_BENCHMARK, 
    CUDA_DETERMINISTIC, 
    ALLOW_TF32, 
    RANDOM_SEED
)

def set_random_seeds(seed=RANDOM_SEED):
    """
    Set random seeds for reproducibility across different libraries
    
    Args:
        seed (int): Random seed value
    """
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

def setup_gpu_optimizations():
    """
    Configure GPU optimization settings for maximum performance
    
    Returns:
        dict: Applied optimization settings
    """
    optimizations = {
        "cudnn_benchmark": False,
        "cudnn_deterministic": True, 
        "tf32_enabled": False,
        "empty_cache_cleared": False
    }
    
    if torch.cuda.is_available():
        # Enable cuDNN benchmark for consistent input sizes (improves performance)
        torch.backends.cudnn.benchmark = CUDA_BENCHMARK
        optimizations["cudnn_benchmark"] = CUDA_BENCHMARK
        
        # Set deterministic behavior (may reduce performance but ensures reproducibility)
        torch.backends.cudnn.deterministic = CUDA_DETERMINISTIC
        optimizations["cudnn_deterministic"] = CUDA_DETERMINISTIC
        
        # Clear GPU cache to start fresh
        torch.cuda.empty_cache()
        optimizations["empty_cache_cleared"] = True
        
        # Enable TensorFloat-32 (TF32) for faster computation on Ampere GPUs
        if ALLOW_TF32 and hasattr(torch.backends.cuda.matmul, 'allow_tf32'):
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            optimizations["tf32_enabled"] = True
    
    return optimizations

def get_device_info():
    """
    Get detailed information about available computing devices
    
    Returns:
        dict: Device information including GPU details
    """
    device_info = {
        "cuda_available": torch.cuda.is_available(),
        "device_count": 0,
        "current_device": None,
        "device_name": None,
        "memory_info": None,
        "compute_capability": None
    }
    
    if torch.cuda.is_available():
        device_info["device_count"] = torch.cuda.device_count()
        device_info["current_device"] = torch.cuda.current_device()
        device_info["device_name"] = torch.cuda.get_device_name(0)
        
        # Get memory information
        memory_allocated = torch.cuda.memory_allocated(0)
        memory_reserved = torch.cuda.memory_reserved(0)
        memory_total = torch.cuda.get_device_properties(0).total_memory
        
        device_info["memory_info"] = {
            "allocated_mb": memory_allocated / 1024**2,
            "reserved_mb": memory_reserved / 1024**2, 
            "total_mb": memory_total / 1024**2,
            "free_mb": (memory_total - memory_reserved) / 1024**2
        }
        
        # Get compute capability
        props = torch.cuda.get_device_properties(0)
        device_info["compute_capability"] = f"{props.major}.{props.minor}"
    
    return device_info

def setup_device():
    """
    Setup and configure the computing device (GPU/CPU)
    
    Returns:
        tuple: (device, device_info, optimizations)
    """
    # Set random seeds first
    set_random_seeds()
    
    # Setup GPU optimizations
    optimizations = setup_gpu_optimizations()
    
    # Get device information
    device_info = get_device_info()
    
    # Select device
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        print(f"    Using GPU: {device_info['device_name']}")
        print(f"   Compute Capability: {device_info['compute_capability']}")
        print(f"   Total Memory: {device_info['memory_info']['total_mb']:.0f} MB")
        print(f"   Free Memory: {device_info['memory_info']['free_mb']:.0f} MB")
    else:
        device = torch.device("cpu")
        print("   CUDA not available. Using CPU.")
        print("   Training will be significantly slower.")
    
    return device, device_info, optimizations

def check_gpu_memory(device, required_gb=4):
    """
    Check if GPU has sufficient memory for training
    
    Args:
        device (torch.device): Computing device
        required_gb (float): Required memory in GB
        
    Returns:
        bool: True if sufficient memory available
    """
    if device.type == 'cpu':
        return True
        
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        total_memory_gb = props.total_memory / 1024**3
        
        if total_memory_gb >= required_gb:
            print(f"GPU Memory Check: {total_memory_gb:.1f} GB available (required: {required_gb} GB)")
            return True
        else:
            print(f"  GPU Memory Warning: {total_memory_gb:.1f} GB available (required: {required_gb} GB)")
            print("   Consider reducing batch size or using a smaller model")
            return False
    
    return False

def clear_gpu_cache():
    """
    Clear GPU cache to free up memory
    """
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("GPU cache cleared")

def print_device_summary():
    """
    Print a comprehensive summary of device configuration
    """
    print("\n" + "="*60)
    print("DEVICE CONFIGURATION SUMMARY")
    print("="*60)
    
    device, device_info, optimizations = setup_device()
    
    print(f"Primary Device: {device}")
    print(f"Random Seed: {RANDOM_SEED}")
    
    if device_info["cuda_available"]:
        print(f"GPU Count: {device_info['device_count']}")
        print(f"Active GPU: {device_info['device_name']}")
        
        print("\nGPU Optimizations:")
        for key, value in optimizations.items():
            print(f"  {key}: {value}")
        
        print("\nMemory Status:")
        mem = device_info["memory_info"]
        print(f"  Total: {mem['total_mb']:.0f} MB")
        print(f"  Free: {mem['free_mb']:.0f} MB")
        print(f"  Allocated: {mem['allocated_mb']:.0f} MB")
        print(f"  Reserved: {mem['reserved_mb']:.0f} MB")
    else:
        print("GPU: Not available")
        print("Fallback: CPU computation")
    
    print("="*60 + "\n")
    
    return device

# Convenience function for easy import
def get_device():
    """
    Simple function to get configured device
    
    Returns:
        torch.device: Configured computing device
    """
    device, _, _ = setup_device()
    return device