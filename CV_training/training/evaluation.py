"""
training/evaluation.py - Evaluation and Metrics Utilities

This module contains:
- Model evaluation functions
- Metrics calculation and reporting
- Visualization utilities for training progress
- Confusion matrix generation
- Performance analysis tools
"""

import torch
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from tqdm import tqdm
from config import FIGURE_SIZE_TRAINING, FIGURE_SIZE_CONFUSION, TARGET_ACCURACY, ZERO_DIVISION_HANDLING

def evaluate_model(model, data_loader, device, class_names, verbose=True):
    """
    Comprehensive model evaluation on given data loader
    
    Args:
        model (torch.nn.Module): Model to evaluate
        data_loader (DataLoader): Data loader for evaluation
        device (torch.device): Device to run evaluation on
        class_names (list): List of class names
        verbose (bool): Whether to print detailed results
        
    Returns:
        tuple: (accuracy, predictions, true_labels)
    """
    model.eval()
    all_predictions = []
    all_labels = []
    all_probabilities = []
    
    if verbose:
        print("🔍 Evaluating model performance...")
    
    with torch.no_grad():
        data_iter = tqdm(data_loader, desc="Evaluating") if verbose else data_loader
        
        for inputs, labels in data_iter:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(inputs)
            probabilities = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs, 1)
            
            # Store results
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probabilities.extend(probabilities.cpu().numpy())
    
    # Convert to numpy arrays
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    all_probabilities = np.array(all_probabilities)
    
    # Calculate accuracy
    accuracy = np.mean(all_predictions == all_labels)
    
    if verbose:
        print(f"\n EVALUATION RESULTS")
        print(f"{'='*50}")
        print(f"Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Target accuracy check
        if accuracy >= TARGET_ACCURACY:
            print(f" Target accuracy ACHIEVED: {accuracy:.1%} >= {TARGET_ACCURACY:.1%}")
        else:
            print(f"  Target accuracy not reached: {accuracy:.1%} < {TARGET_ACCURACY:.1%}")
        
        # Detailed classification report
        print(f"\n DETAILED CLASSIFICATION REPORT")
        print(f"{'='*50}")
        try:
            report = classification_report(
                all_labels, 
                all_predictions, 
                target_names=class_names,
                zero_division=ZERO_DIVISION_HANDLING,
                digits=4
            )
            print(report)
        except Exception as e:
            print(f" Error generating classification report: {e}")
        
        # Per-class accuracy
        print(f"\n PER-CLASS ACCURACY")
        print(f"{'='*50}")
        for i, class_name in enumerate(class_names):
            class_mask = all_labels == i
            if np.sum(class_mask) > 0:
                class_acc = np.mean(all_predictions[class_mask] == all_labels[class_mask])
                class_count = np.sum(class_mask)
                print(f"{class_name:20s}: {class_acc:.4f} ({class_acc*100:.1f}%) | {class_count} samples")
        
        # Confusion matrix
        print(f"\n GENERATING CONFUSION MATRIX")
        print(f"{'='*50}")
        create_confusion_matrix(all_labels, all_predictions, class_names)
    
    return accuracy, all_predictions, all_labels

def calculate_metrics(true_labels, predictions, class_names, average='weighted'):
    """
    Calculate comprehensive metrics for multi-class classification
    
    Args:
        true_labels (array): True class labels
        predictions (array): Predicted class labels
        class_names (list): List of class names
        average (str): Averaging method for metrics
        
    Returns:
        dict: Dictionary of calculated metrics
    """
    # Basic accuracy
    accuracy = np.mean(true_labels == predictions)
    
    # Precision, recall, F1-score
    precision, recall, f1, support = precision_recall_fscore_support(
        true_labels, predictions, average=average, zero_division=0
    )
    
    # Per-class metrics
    per_class_precision, per_class_recall, per_class_f1, per_class_support = precision_recall_fscore_support(
        true_labels, predictions, average=None, zero_division=0
    )
    
    # Calculate per-class accuracy
    per_class_accuracy = []
    for i in range(len(class_names)):
        class_mask = true_labels == i
        if np.sum(class_mask) > 0:
            class_acc = np.mean(predictions[class_mask] == true_labels[class_mask])
        else:
            class_acc = 0.0
        per_class_accuracy.append(class_acc)
    
    metrics = {
        'overall_accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'per_class_metrics': {
            'accuracy': per_class_accuracy,
            'precision': per_class_precision.tolist(),
            'recall': per_class_recall.tolist(),
            'f1_score': per_class_f1.tolist(),
            'support': per_class_support.tolist()
        },
        'class_names': class_names
    }
    
    return metrics

def plot_training_history(history, save_path=None):
    """
    Plot training history with loss and accuracy curves
    
    Args:
        history (dict): Training history containing loss and accuracy
        save_path (str, optional): Path to save the plot
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    epochs = range(1, len(history['train_loss']) + 1)
    
    # Plot 1: Loss curves
    axes[0].plot(epochs, history['train_loss'], 'b-', label='Training Loss', linewidth=2)
    axes[0].plot(epochs, history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
    axes[0].set_title('Model Loss', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Add loss statistics
    min_train_loss = min(history['train_loss'])
    min_val_loss = min(history['val_loss'])
    axes[0].text(0.02, 0.98, f'Min Train Loss: {min_train_loss:.4f}\nMin Val Loss: {min_val_loss:.4f}', 
                transform=axes[0].transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Plot 2: Accuracy curves
    axes[1].plot(epochs, history['train_acc'], 'b-', label='Training Accuracy', linewidth=2)
    axes[1].plot(epochs, history['val_acc'], 'r-', label='Validation Accuracy', linewidth=2)
    axes[1].set_title('Model Accuracy', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Add accuracy statistics
    max_train_acc = max(history['train_acc'])
    max_val_acc = max(history['val_acc'])
    axes[1].text(0.02, 0.98, f'Max Train Acc: {max_train_acc:.4f}\nMax Val Acc: {max_val_acc:.4f}', 
                transform=axes[1].transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Plot 3: Learning rate curve
    if 'learning_rates' in history and history['learning_rates']:
        axes[2].plot(epochs, history['learning_rates'], 'g-', label='Learning Rate', linewidth=2)
        axes[2].set_title('Learning Rate Schedule', fontsize=14, fontweight='bold')
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('Learning Rate')
        axes[2].set_yscale('log')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
    else:
        # If no learning rate data, show validation accuracy zoomed
        axes[2].plot(epochs, history['val_acc'], 'purple', label='Validation Accuracy', linewidth=3)
        axes[2].set_title('Validation Accuracy (Detailed)', fontsize=14, fontweight='bold')
        axes[2].set_xlabel('Epoch')
        axes[2].set_ylabel('Accuracy')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        # Add target line if available
        if TARGET_ACCURACY:
            axes[2].axhline(y=TARGET_ACCURACY, color='red', linestyle='--', alpha=0.7, label=f'Target ({TARGET_ACCURACY:.2f})')
            axes[2].legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f" Training history plot saved: {save_path}")
    
    plt.show()

def create_confusion_matrix(true_labels, predictions, class_names, normalize=True, save_path=None):
    """
    Create and display confusion matrix
    
    Args:
        true_labels (array): True class labels
        predictions (array): Predicted class labels
        class_names (list): List of class names
        normalize (bool): Whether to normalize the matrix
        save_path (str, optional): Path to save the plot
    """
    # Calculate confusion matrix
    cm = confusion_matrix(true_labels, predictions)
    
    if normalize:
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm_display = cm_normalized
        fmt = '.2f'
        title = 'Normalized Confusion Matrix'
    else:
        cm_display = cm
        fmt = 'd'
        title = 'Confusion Matrix'
    
    # Create plot
    plt.figure(figsize=FIGURE_SIZE_CONFUSION)
    
    # Use a better color map
    sns.heatmap(cm_display, 
                annot=True, 
                fmt=fmt, 
                cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names,
                cbar_kws={'label': 'Proportion' if normalize else 'Count'})
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Add text annotations for raw counts if normalized
    if normalize:
        for i in range(len(class_names)):
            for j in range(len(class_names)):
                plt.text(j + 0.5, i + 0.7, f'({cm[i, j]})', 
                        ha='center', va='center', fontsize=8, color='gray')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f" Confusion matrix saved: {save_path}")
    
    plt.show()
    
    # Print confusion matrix statistics
    print(f"\n Confusion Matrix Statistics:")
    print(f"{'='*40}")
    
    # Diagonal accuracy (correct predictions)
    diagonal_sum = np.trace(cm)
    total_sum = np.sum(cm)
    accuracy = diagonal_sum / total_sum
    print(f"Overall Accuracy: {accuracy:.4f}")
    
    # Per-class statistics
    for i, class_name in enumerate(class_names):
        true_positives = cm[i, i]
        false_positives = np.sum(cm[:, i]) - true_positives
        false_negatives = np.sum(cm[i, :]) - true_positives
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        
        print(f"{class_name:15s}: Precision={precision:.3f}, Recall={recall:.3f}")

def plot_class_performance(metrics, save_path=None):
    """
    Plot per-class performance metrics
    
    Args:
        metrics (dict): Metrics dictionary from calculate_metrics
        save_path (str, optional): Path to save the plot
    """
    class_names = metrics['class_names']
    per_class = metrics['per_class_metrics']
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    x_pos = np.arange(len(class_names))
    
    # Plot 1: Per-class Accuracy
    axes[0, 0].bar(x_pos, per_class['accuracy'], alpha=0.7, color='skyblue', edgecolor='navy')
    axes[0, 0].set_title('Per-Class Accuracy', fontweight='bold')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(class_names, rotation=45, ha='right')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate(per_class['accuracy']):
        axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Per-class Precision
    axes[0, 1].bar(x_pos, per_class['precision'], alpha=0.7, color='lightgreen', edgecolor='darkgreen')
    axes[0, 1].set_title('Per-Class Precision', fontweight='bold')
    axes[0, 1].set_ylabel('Precision')
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(class_names, rotation=45, ha='right')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Plot 3: Per-class Recall
    axes[1, 0].bar(x_pos, per_class['recall'], alpha=0.7, color='lightcoral', edgecolor='darkred')
    axes[1, 0].set_title('Per-Class Recall', fontweight='bold')
    axes[1, 0].set_ylabel('Recall')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(class_names, rotation=45, ha='right')
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Plot 4: Per-class F1-Score
    axes[1, 1].bar(x_pos, per_class['f1_score'], alpha=0.7, color='gold', edgecolor='orange')
    axes[1, 1].set_title('Per-Class F1-Score', fontweight='bold')
    axes[1, 1].set_ylabel('F1-Score')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(class_names, rotation=45, ha='right')
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f" Class performance plot saved: {save_path}")
    
    plt.show()

def analyze_model_performance(model, data_loader, device, class_names, save_dir=None):
    """
    Comprehensive model performance analysis
    
    Args:
        model: Trained model
        data_loader: Data loader for evaluation
        device: Computing device
        class_names: List of class names
        save_dir: Directory to save analysis plots
        
    Returns:
        dict: Comprehensive analysis results
    """
    print(f"\n COMPREHENSIVE PERFORMANCE ANALYSIS")
    print(f"{'='*60}")
    
    # Basic evaluation
    accuracy, predictions, true_labels = evaluate_model(model, data_loader, device, class_names)
    
    # Calculate detailed metrics
    metrics = calculate_metrics(true_labels, predictions, class_names)
    
    # Generate plots
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        confusion_path = os.path.join(save_dir, 'confusion_matrix.png')
        performance_path = os.path.join(save_dir, 'class_performance.png')
    else:
        confusion_path = None
        performance_path = None
    
    # Create visualizations
    create_confusion_matrix(true_labels, predictions, class_names, save_path=confusion_path)
    plot_class_performance(metrics, save_path=performance_path)
    
    # Analysis summary
    analysis_results = {
        'overall_accuracy': accuracy,
        'metrics': metrics,
        'predictions': predictions,
        'true_labels': true_labels,
        'analysis_summary': {
            'total_samples': len(true_labels),
            'correct_predictions': np.sum(predictions == true_labels),
            'target_achieved': accuracy >= TARGET_ACCURACY,
            'best_performing_class': class_names[np.argmax(metrics['per_class_metrics']['accuracy'])],
            'worst_performing_class': class_names[np.argmin(metrics['per_class_metrics']['accuracy'])],
            'average_f1_score': np.mean(metrics['per_class_metrics']['f1_score'])
        }
    }
    
    # Print summary
    summary = analysis_results['analysis_summary']
    print(f"\n ANALYSIS SUMMARY")
    print(f"{'='*40}")
    print(f"Total samples: {summary['total_samples']}")
    print(f"Correct predictions: {summary['correct_predictions']}")
    print(f"Overall accuracy: {accuracy:.4f}")
    print(f"Average F1-score: {summary['average_f1_score']:.4f}")
    print(f"Target achieved: {summary['target_achieved']}")
    print(f"Best class: {summary['best_performing_class']}")
    print(f"Worst class: {summary['worst_performing_class']}")
    
    return analysis_results

def compare_models(model_results_list, model_names, metric='accuracy'):
    """
    Compare performance of multiple models
    
    Args:
        model_results_list: List of model evaluation results
        model_names: List of model names
        metric: Metric to compare ('accuracy', 'f1_score', 'precision', 'recall')
    """
    plt.figure(figsize=(12, 6))
    
    if metric == 'accuracy':
        values = [results['overall_accuracy'] for results in model_results_list]
        ylabel = 'Accuracy'
    else:
        values = [results['metrics'][metric] for results in model_results_list]
        ylabel = metric.replace('_', ' ').title()
    
    bars = plt.bar(model_names, values, alpha=0.7, color=['skyblue', 'lightgreen', 'lightcoral', 'gold'][:len(model_names)])
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.title(f'Model Comparison - {ylabel}', fontsize=16, fontweight='bold')
    plt.ylabel(ylabel)
    plt.xlabel('Models')
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Add horizontal line at target if comparing accuracy
    if metric == 'accuracy' and TARGET_ACCURACY:
        plt.axhline(y=TARGET_ACCURACY, color='red', linestyle='--', alpha=0.7, 
                   label=f'Target ({TARGET_ACCURACY:.2f})')
        plt.legend()
    
    plt.tight_layout()
    plt.show()

def print_evaluation_summary(accuracy, class_names, training_time=None):
    """
    Print a comprehensive evaluation summary
    
    Args:
        accuracy: Model accuracy
        class_names: List of class names
        training_time: Training time in seconds (optional)
    """
    print(f"\n" + "="*70)
    print(f" FINAL EVALUATION SUMMARY")
    print(f"="*70)
    
    print(f" Model Performance:")
    print(f"   Final Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    if accuracy >= TARGET_ACCURACY:
        print(f"    TARGET ACHIEVED: {accuracy:.1%} >= {TARGET_ACCURACY:.1%}")
    else:
        print(f"     Target not reached: {accuracy:.1%} < {TARGET_ACCURACY:.1%}")
    
    print(f"\n Dataset Information:")
    print(f"   Number of classes: {len(class_names)}")
    print(f"   Class names: {', '.join(class_names)}")
    
    if training_time:
        print(f"\n⏱️  Training Information:")
        print(f"   Training time: {training_time/60:.1f} minutes")
        print(f"   Training efficiency: {accuracy/(training_time/3600):.2f} accuracy/hour")
    
    # Performance interpretation
    print(f"\n Performance Interpretation:")
    if accuracy >= 0.95:
        print(f"    Excellent performance - Model is highly accurate")
    elif accuracy >= 0.90:
        print(f"    Very good performance - Model meets target requirements")
    elif accuracy >= 0.80:
        print(f"     Good performance - Model is reasonably accurate")
    elif accuracy >= 0.70:
        print(f"     Fair performance - Consider model improvements")
    else:
        print(f"    Poor performance - Significant improvements needed")
    
    print(f"="*70)