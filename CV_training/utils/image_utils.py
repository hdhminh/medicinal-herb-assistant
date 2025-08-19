"""
utils/image_utils.py - Image Processing and AVIF Handling Utilities

This module handles:
- Robust image loading for various formats
- AVIF format detection and conversion
- Image format identification
- Dataset cleaning and preprocessing
- Error handling for corrupted images
"""

import os
import cv2
import warnings
import numpy as np
from PIL import Image, ImageFile
from config import SUPPORTED_EXTENSIONS, JPEG_QUALITY

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

def identify_image_format(image_path):
    """
    Identify actual image format from file header bytes
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Detected image format ('JPEG', 'PNG', 'BMP', 'WEBP', 'AVIF', 'Unknown', 'Error')
    """
    try:
        with open(image_path, 'rb') as f:
            header = f.read(12)
        
        # Check file headers/magic numbers
        if header[:2] == b'\xff\xd8':
            return 'JPEG'
        elif header[:8] == b'\x89PNG\r\n\x1a\n':
            return 'PNG'
        elif header[:2] in [b'BM', b'BA']:
            return 'BMP'
        elif header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return 'WEBP'
        elif header[:4] == b'\x00\x00\x00 ' or header[:4] == b'\x00\x00\x00\x1c':
            return 'AVIF'  # AVIF file signature
        else:
            return 'Unknown'
    except Exception as e:
        print(f"Error reading file header for {image_path}: {e}")
        return 'Error'

def load_image_robust(img_path):
    """
    Enhanced robust image loading with better AVIF support
    """
    # Strategy 1: Try PIL with pillow-avif
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            img = Image.open(img_path)
            img.load()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            return img
    except Exception:
        pass
    
    # Strategy 2: Force AVIF loading
    try:
        import pillow_avif
        # Register AVIF plugin
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        
        img = Image.open(img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception:
        pass
    
    # Strategy 3: Use imageio for AVIF
    try:
        import imageio.v3 as iio
        img_array = iio.imread(img_path)
        if len(img_array.shape) == 2:
            img_array = np.stack([img_array] * 3, axis=-1)
        img = Image.fromarray(img_array.astype('uint8'))
        return img
    except Exception:
        pass
    
    # Strategy 4: OpenCV fallback
    try:
        img_cv = cv2.imread(img_path)
        if img_cv is not None:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            return Image.fromarray(img_cv)
    except Exception:
        pass
    
    return None

def clean_dataset(data_path, verbose=True):
    """
    Analyze dataset without removing files, identify format issues
    
    Args:
        data_path (str): Path to dataset root directory
        verbose (bool): Whether to print detailed information
        
    Returns:
        dict: Summary of dataset analysis
    """
    if verbose:
        print("="*50)
        print("DATASET ANALYSIS (READ-ONLY)")
        print("="*50)
    
    analysis = {
        'total_files': 0,
        'avif_disguised': 0,
        'format_issues': {},
        'unknown_formats': 0,
        'classes': []
    }
    
    for class_name in os.listdir(data_path):
        class_path = os.path.join(data_path, class_name)
        if not os.path.isdir(class_path):
            continue
        
        analysis['classes'].append(class_name)
        class_issues = []
        
        for img_file in os.listdir(class_path):
            if img_file.lower().endswith(SUPPORTED_EXTENSIONS):
                analysis['total_files'] += 1
                img_path = os.path.join(class_path, img_file)
                
                # Check actual format vs extension
                actual_format = identify_image_format(img_path)
                extension = os.path.splitext(img_file)[1].lower()
                
                # Identify format mismatches
                if actual_format == 'AVIF' and extension in ['.jpg', '.jpeg']:
                    analysis['avif_disguised'] += 1
                    class_issues.append(f"{img_file} is actually AVIF but has .jpg extension")
                elif actual_format == 'Unknown':
                    analysis['unknown_formats'] += 1
                    class_issues.append(f"{img_file} has unknown/unrecognizable format")
                elif actual_format == 'Error':
                    class_issues.append(f"{img_file} could not be read (corrupted?)")
        
        if class_issues:
            analysis['format_issues'][class_name] = class_issues
    
    if verbose:
        print(f"Total files checked: {analysis['total_files']}")
        print(f"Classes found: {len(analysis['classes'])}")
        print(f"AVIF files with .jpg extension: {analysis['avif_disguised']}")
        print(f"Unknown format files: {analysis['unknown_formats']}")
        
        if analysis['format_issues']:
            print("\nFormat Issues by Class:")
            for class_name, issues in analysis['format_issues'].items():
                print(f"  {class_name}: {len(issues)} issues")
        else:
            print("No format issues detected")
        
        print("="*50)
    
    return analysis

def convert_disguised_avif_to_jpg(data_path, save_over=True, verbose=True):
    """
    Convert images with AVIF content but wrong extensions to proper JPEG files
    
    Args:
        data_path (str): Path to dataset root directory
        save_over (bool): Whether to overwrite original files
        verbose (bool): Whether to print conversion progress
        
    Returns:
        int: Number of files successfully converted
    """
    if verbose:
        print("="*50)
        print("AVIF TO JPEG CONVERSION")
        print("="*50)
    
    converted = 0
    failed = 0

    for class_name in os.listdir(data_path):
        class_path = os.path.join(data_path, class_name)
        if not os.path.isdir(class_path):
            continue

        for img_file in os.listdir(class_path):
            ext = os.path.splitext(img_file)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.avif']:
                img_path = os.path.join(class_path, img_file)
                fmt = identify_image_format(img_path)

                if fmt == 'AVIF':
                    try:
                        img = load_image_robust(img_path)
                        if img:
                            # Determine output path
                            if save_over:
                                new_path = img_path
                            else:
                                new_name = os.path.splitext(img_path)[0]
                                new_path = new_name + "_converted.jpg"
                            
                            # Save as JPEG
                            img.save(new_path, "JPEG", quality=JPEG_QUALITY)
                            converted += 1
                            
                            if verbose:
                                print(f"  {img_file} → {os.path.basename(new_path)}")
                        else:
                            failed += 1
                            if verbose:
                                print(f"  Failed to load {img_file}")
                    except Exception as e:
                        failed += 1
                        if verbose:
                            print(f"  Error converting {img_file}: {e}")

    if verbose:
        print(f"\n Conversion complete:")
        print(f"   Successfully converted: {converted} files")
        print(f"   Failed conversions: {failed} files")
        print("="*50)
    
    return converted

def create_placeholder_image(class_label, img_size=(224, 224)):
    """
    Create a placeholder image with class-specific pattern for failed loads
    
    Args:
        class_label (int): Class index for pattern generation
        img_size (tuple): Target image size
        
    Returns:
        PIL.Image: Generated placeholder image
    """
    # Create black base image
    image = Image.new('RGB', img_size, color='black')
    pixels = image.load()
    
    # Add class-specific pattern
    pattern_size = 20
    color_val = (class_label * 30) % 255
    
    for i in range(0, img_size[0], pattern_size):
        for j in range(0, img_size[1], pattern_size):
            # Create a unique color pattern for each class
            r = (color_val + i // pattern_size) % 255
            g = (color_val + 50 + j // pattern_size) % 255
            b = (color_val + 100) % 255
            
            # Draw a small square pattern
            for di in range(min(pattern_size//2, img_size[0] - i)):
                for dj in range(min(pattern_size//2, img_size[1] - j)):
                    if i + di < img_size[0] and j + dj < img_size[1]:
                        pixels[i + di, j + dj] = (r, g, b)
    
    return image

def validate_image_file(img_path):
    """
    Validate if an image file can be loaded successfully
    
    Args:
        img_path (str): Path to image file
        
    Returns:
        tuple: (is_valid, error_message, format_info)
    """
    try:
        # Check if file exists
        if not os.path.exists(img_path):
            return False, "File does not exist", None
        
        # Check file size
        file_size = os.path.getsize(img_path)
        if file_size == 0:
            return False, "File is empty", None
        
        # Identify format
        actual_format = identify_image_format(img_path)
        if actual_format == 'Error':
            return False, "Cannot read file header", None
        
        # Try to load image
        img = load_image_robust(img_path)
        if img is None:
            return False, f"Cannot load image (detected format: {actual_format})", actual_format
        
        # Check image properties
        if img.size[0] == 0 or img.size[1] == 0:
            return False, "Image has zero dimensions", actual_format
        
        return True, "Valid image", actual_format
        
    except Exception as e:
        return False, f"Validation error: {str(e)}", None

def batch_validate_images(data_path, verbose=True):
    """
    Validate all images in the dataset
    
    Args:
        data_path (str): Path to dataset root directory
        verbose (bool): Whether to print detailed results
        
    Returns:
        dict: Validation results summary
    """
    if verbose:
        print("="*50)
        print("BATCH IMAGE VALIDATION")
        print("="*50)
    
    results = {
        'total_checked': 0,
        'valid_images': 0,
        'invalid_images': 0,
        'errors_by_type': {},
        'invalid_files': []
    }
    
    for class_name in os.listdir(data_path):
        class_path = os.path.join(data_path, class_name)
        if not os.path.isdir(class_path):
            continue
        
        for img_file in os.listdir(class_path):
            if img_file.lower().endswith(SUPPORTED_EXTENSIONS):
                img_path = os.path.join(class_path, img_file)
                results['total_checked'] += 1
                
                is_valid, error_msg, format_info = validate_image_file(img_path)
                
                if is_valid:
                    results['valid_images'] += 1
                else:
                    results['invalid_images'] += 1
                    results['invalid_files'].append({
                        'path': img_path,
                        'error': error_msg,
                        'format': format_info
                    })
                    
                    # Track error types
                    error_type = error_msg.split(':')[0] if ':' in error_msg else error_msg
                    results['errors_by_type'][error_type] = results['errors_by_type'].get(error_type, 0) + 1
    
    if verbose:
        print(f"Total files checked: {results['total_checked']}")
        print(f"Valid images: {results['valid_images']}")
        print(f"Invalid images: {results['invalid_images']}")
        
        if results['errors_by_type']:
            print("\nError types:")
            for error_type, count in results['errors_by_type'].items():
                print(f"  {error_type}: {count}")
        
        if results['invalid_files'] and verbose:
            print(f"\nFirst 5 invalid files:")
            for i, invalid_file in enumerate(results['invalid_files'][:5]):
                print(f"  {i+1}. {os.path.basename(invalid_file['path'])}: {invalid_file['error']}")
        
        print("="*50)
    
    return results

def get_image_statistics(data_path):
    """
    Gather statistics about images in the dataset
    
    Args:
        data_path (str): Path to dataset root directory
        
    Returns:
        dict: Image statistics
    """
    stats = {
        'total_images': 0,
        'image_sizes': [],
        'file_sizes': [],
        'formats': {},
        'classes': {}
    }
    
    for class_name in os.listdir(data_path):
        class_path = os.path.join(data_path, class_name)
        if not os.path.isdir(class_path):
            continue
        
        class_count = 0
        for img_file in os.listdir(class_path):
            if img_file.lower().endswith(SUPPORTED_EXTENSIONS):
                img_path = os.path.join(class_path, img_file)
                
                # Count total images
                stats['total_images'] += 1
                class_count += 1
                
                # Get file size
                file_size = os.path.getsize(img_path)
                stats['file_sizes'].append(file_size)
                
                # Get image format
                img_format = identify_image_format(img_path)
                stats['formats'][img_format] = stats['formats'].get(img_format, 0) + 1
                
                # Try to get image dimensions
                try:
                    img = load_image_robust(img_path)
                    if img:
                        stats['image_sizes'].append(img.size)
                except:
                    pass
        
        stats['classes'][class_name] = class_count
    
    return stats