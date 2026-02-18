"""
Training script - Copy to: train_model.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.ml.vit_model import ViTModel, ModelCheckpoint
import tensorflow as tf
import numpy as np

def train_with_dummy():
    print(" Training with dummy data (for testing)...")
    
    # Create dummy data
    train_images = np.random.randint(0, 256, (100, 224, 224, 3), dtype=np.uint8) / 255.0
    train_labels = np.random.randint(0, 10, 100)
    
    val_images = np.random.randint(0, 256, (20, 224, 224, 3), dtype=np.uint8) / 255.0
    val_labels = np.random.randint(0, 10, 20)
    
    train_ds = tf.data.Dataset.from_tensor_slices((train_images, train_labels)).batch(16)
    val_ds = tf.data.Dataset.from_tensor_slices((val_images, val_labels)).batch(16)
    
    # Create model
    vit = ViTModel(num_classes=10)
    
    # Setup checkpoints
    checkpoint = ModelCheckpoint()
    
    # Train
    vit.model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=3,
        callbacks=checkpoint.get_callbacks()
    )
    
    print(" Training complete!")

if __name__ == "__main__":
    train_with_dummy()