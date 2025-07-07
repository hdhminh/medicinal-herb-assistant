"""
main.py - Main Entry Point for Herb Recognition CV Pipeline

This script orchestrates the complete machine learning pipeline:
1. Dataset analysis and preprocessing
2. Model creation and configuration
3. Training with monitoring and early stopping
4. Evaluation and visualization
5. Model saving and metadata export

Usage:
    python main.py
    
Configuration can be modified in config.py
"""

import os
import sys
import argparse
import warnings
import time
from datetime import datetime

# Import custom modules
from config import *
from utils.gpu_setup import print_device_summary
from utils.image_utils import clean_dataset, convert_disguised_avif_to_jpg
from utils.data_utils import print_dataset_summary
from training.trainer import HerbRecognitionCV

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Herb Recognition Computer Vision Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Data arguments
    parser.add_argument('--data-path', type=str, default=DATA_PATH,
                       help='Path to dataset directory')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                       help='Batch size for training')
    
    # Model arguments
    parser.add_argument('--model', type=str, default=MODEL_TYPE,
                       choices=['dinov2_vits14', 'dinov2_vitb14', 'dinov2_vitl14', 
                               'dinov2_vitg14', 'custom_cnn'],
                       help='Model architecture to use')
    
    # Training arguments
    parser.add_argument('--epochs', type=int, default=EPOCHS,
                       help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=LEARNING_RATE,
                       help='Learning rate')
    parser.add_argument('--patience', type=int, default=PATIENCE,
                       help='Early stopping patience')
    
    # Preprocessing arguments
    parser.add_argument('--skip-conversion', action='store_true',
                       help='Skip AVIF to JPEG conversion')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Skip dataset analysis')
    
    # Execution control
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without training (analysis only)')
    parser.add_argument('--quick-test', action='store_true',
                       help='Quick test with reduced parameters')
    
    return parser.parse_args()

def print_pipeline_header():
    """Print pipeline header with timestamp"""
    print("="*80)
    print("🌿 HERB RECOGNITION COMPUTER VISION PIPELINE 🌿")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {sys.version}")
    print("="*80)

def validate_setup(args):
    """
    Validate setup and configuration
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        bool: True if setup is valid
    """
    print("\n🔍 VALIDATING SETUP")
    print("-" * 40)
    
    # Check data path
    if not os.path.exists(args.data_path):
        print(f"❌ Data path does not exist: {args.data_path}")
        return False
    print(f"✅ Data path found: {args.data_path}")
    
    # Check if data path contains subdirectories (classes)
    subdirs = [d for d in os.listdir(args.data_path) 
               if os.path.isdir(os.path.join(args.data_path, d))]
    if not subdirs:
        print(f"❌ No class directories found in {args.data_path}")
        return False
    print(f"✅ Found {len(subdirs)} class directories")
    
    # Check save directory
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"✅ Save directory ready: {SAVE_DIR}")
    
    # Validate model choice
    if args.model.startswith('dinov2'):
        try:
            import torch.hub
            print(f"✅ Model {args.model} available")
        except ImportError:
            print("❌ PyTorch Hub not available for DINOv2 models")
            return False
    
    print("✅ Setup validation complete\n")
    return True

def run_preprocessing(args):
    """
    Run data preprocessing steps
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        dict: Preprocessing results
    """
    print("🔧 PREPROCESSING PHASE")
    print("-" * 40)
    
    results = {}
    
    # Dataset analysis
    if not args.skip_analysis:
        print("\n📊 Analyzing dataset structure...")
        analysis = clean_dataset(args.data_path, verbose=True)
        results['dataset_analysis'] = analysis
        
        # Print summary
        print_dataset_summary(args.data_path)
    
    # AVIF conversion
    if not args.skip_conversion and CONVERT_AVIF_TO_JPEG:
        print("\n🔄 Converting AVIF files to JPEG...")
        converted_count = convert_disguised_avif_to_jpg(
            args.data_path, 
            save_over=SAVE_OVER_ORIGINAL,
            verbose=True
        )
        results['converted_files'] = converted_count
        
        if converted_count > 0:
            print(f"✅ Converted {converted_count} AVIF files to JPEG")
        else:
            print("ℹ️  No AVIF files found for conversion")
    
    print("\n✅ Preprocessing complete\n")
    return results

def create_training_system(args):
    """
    Create and configure the training system
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        HerbRecognitionCV: Configured training system
    """
    print("🏗️  CREATING TRAINING SYSTEM")
    print("-" * 40)
    
    # Adjust parameters for quick test
    batch_size = args.batch_size
    num_workers = NUM_WORKERS
    
    if args.quick_test:
        print("⚡ Quick test mode enabled - reducing parameters")
        batch_size = min(8, batch_size)
        num_workers = 0
    
    # Create training system
    print(f"📦 Initializing training system...")
    print(f"   Data path: {args.data_path}")
    print(f"   Batch size: {batch_size}")
    print(f"   Image size: {IMG_SIZE}")
    
    herb_cv = HerbRecognitionCV(
        data_path=args.data_path,
        img_size=IMG_SIZE,
        batch_size=batch_size,
        num_workers=num_workers
    )
    
    print("✅ Training system created\n")
    return herb_cv

def run_training_pipeline(herb_cv, args):
    """
    Run the complete training pipeline
    
    Args:
        herb_cv: Training system instance
        args: Parsed command line arguments
        
    Returns:
        dict: Training results
    """
    results = {}
    
    # Dataset exploration
    print("🔍 DATASET EXPLORATION")
    print("-" * 40)
    class_counts = herb_cv.explore_dataset()
    herb_cv.visualize_samples()
    results['class_counts'] = class_counts
    
    # Create data loaders
    print("\n📊 CREATING DATA LOADERS")
    print("-" * 40)
    herb_cv.create_data_loaders(validation_split=VALIDATION_SPLIT)
    
    # Build model
    print(f"\n🧠 BUILDING MODEL: {args.model}")
    print("-" * 40)
    model = herb_cv.build_model(model_type=args.model)
    results['model_info'] = herb_cv.get_model_summary()
    
    # Training phase
    if not args.dry_run:
        print(f"\n🚀 TRAINING PHASE")
        print("-" * 40)
        
        # Adjust training parameters for quick test
        epochs = args.epochs
        if args.quick_test:
            epochs = min(5, epochs)
            print(f"⚡ Quick test: reducing epochs to {epochs}")
        
        # Start training
        start_time = time.time()
        history = herb_cv.train_model(
            epochs=epochs,
            learning_rate=args.lr,
            patience=args.patience
        )
        training_time = time.time() - start_time
        
        results['training_history'] = history
        results['training_time'] = training_time
        
        print(f"\n⏱️  Training completed in {training_time/60:.1f} minutes")
        
        # Plot training history
        print("\n📈 PLOTTING TRAINING HISTORY")
        print("-" * 40)
        herb_cv.plot_training_history()
        
        # Evaluation
        print("\n📊 MODEL EVALUATION")
        print("-" * 40)
        accuracy, predictions, labels = herb_cv.evaluate_model()
        results['final_accuracy'] = accuracy
        results['predictions'] = predictions
        results['labels'] = labels
        
        # Check if target accuracy achieved
        target_achieved = accuracy >= TARGET_ACCURACY
        results['target_achieved'] = target_achieved
        
        if target_achieved:
            print(f"🎯 Target accuracy ACHIEVED: {accuracy:.1%} >= {TARGET_ACCURACY:.1%}")
        else:
            print(f"⚠️  Target accuracy NOT achieved: {accuracy:.1%} < {TARGET_ACCURACY:.1%}")
        
        # Save model and metadata
        print("\n💾 SAVING MODEL")
        print("-" * 40)
        herb_cv.save_model_and_metadata(MODEL_SAVE_PATH)
        
    else:
        print("\n🏃 DRY RUN - Skipping training phase")
        results['dry_run'] = True
    
    return results

def print_pipeline_summary(results, start_time):
    """
    Print comprehensive pipeline summary
    
    Args:
        results: Pipeline results dictionary
        start_time: Pipeline start time
    """
    total_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("📋 PIPELINE EXECUTION SUMMARY")
    print("="*80)
    
    print(f"⏱️  Total execution time: {total_time/60:.1f} minutes")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Dataset information
    if 'class_counts' in results:
        class_counts = results['class_counts']
        total_images = sum(class_counts.values())
        print(f"\n📊 Dataset Information:")
        print(f"   Classes: {len(class_counts)}")
        print(f"   Total images: {total_images}")
        print(f"   Images per class: {total_images/len(class_counts):.1f} avg")
    
    # Preprocessing results
    if 'converted_files' in results:
        print(f"\n🔄 Preprocessing:")
        print(f"   AVIF files converted: {results['converted_files']}")
    
    # Training results
    if 'training_time' in results:
        print(f"\n🚀 Training Results:")
        print(f"   Training time: {results['training_time']/60:.1f} minutes")
        print(f"   Final accuracy: {results['final_accuracy']:.1%}")
        print(f"   Target achieved: {'✅ Yes' if results['target_achieved'] else '❌ No'}")
    
    # Model information
    if 'model_info' in results:
        model_info = results['model_info']
        print(f"\n🧠 Model Information:")
        print(f"   Architecture: {model_info.get('model_name', 'Unknown')}")
        print(f"   Total parameters: {model_info.get('total_parameters', 0):,}")
        print(f"   Model size: {model_info.get('model_size_mb', 0):.1f} MB")
    
    # Files created
    print(f"\n📁 Output Files:")
    if os.path.exists(MODEL_SAVE_PATH):
        print(f"   ✅ Model: {MODEL_SAVE_PATH}")
    if os.path.exists(METADATA_PATH):
        print(f"   ✅ Metadata: {METADATA_PATH}")
    if os.path.exists(HISTORY_PATH):
        print(f"   ✅ History: {HISTORY_PATH}")
    
    print("\n🎉 Pipeline execution completed!")
    print("="*80)

def main():
    """
    Main function - orchestrates the entire pipeline
    """
    start_time = time.time()
    
    # Parse arguments
    args = parse_arguments()
    
    # Print header
    print_pipeline_header()
    
    # Print configuration
    print_config()
    
    # Setup device and GPU
    device = print_device_summary()
    
    try:
        # Validate setup
        if not validate_setup(args):
            print("❌ Setup validation failed. Exiting.")
            sys.exit(1)
        
        # Run preprocessing
        preprocessing_results = run_preprocessing(args)
        
        # Create training system
        herb_cv = create_training_system(args)
        
        # Run training pipeline
        training_results = run_training_pipeline(herb_cv, args)
        
        # Combine results
        results = {**preprocessing_results, **training_results}
        
        # Print summary
        print_pipeline_summary(results, start_time)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)