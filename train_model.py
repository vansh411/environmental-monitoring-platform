"""
Training script - Copy to: train_model.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.ml.vit_model import ViTModel, ModelCheckpoint
import tensorflow as tf


# Path to your dataset
DATASET_PATH = Path("data/eurosat/EuroSAT")


def load_eurosat_dataset():
    print("Loading EuroSAT dataset from:", DATASET_PATH)

    # Load training split
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_PATH,
        labels="inferred",
        label_mode="int",
        image_size=(224, 224),
        batch_size=32,
        shuffle=True,
        validation_split=0.2,
        subset="training",
        seed=42
    )

    # Load validation split
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_PATH,
        labels="inferred",
        label_mode="int",
        image_size=(224, 224),
        batch_size=32,
        shuffle=True,
        validation_split=0.2,
        subset="validation",
        seed=42
    )

    # Normalize images to [0,1]
    def normalize(image, label):
        image = tf.cast(image, tf.float32) / 255.0
        return image, label

    train_ds = train_ds.map(normalize)
    val_ds = val_ds.map(normalize)

    return train_ds, val_ds


def train_eurosat():
    print("\n========================================")
    print(" TRAINING VISION TRANSFORMER ON EUROSAT")
    print("========================================\n")

    # Load dataset
    train_ds, val_ds = load_eurosat_dataset()

    # Create model
    vit = ViTModel(num_classes=10)

    # Setup checkpoints
    checkpoint = ModelCheckpoint()

    # Train model
    vit.model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=20,
        callbacks=checkpoint.get_callbacks()
    )

    # Save final trained model
    save_path = "./models/eurosat_vit.keras"
    vit.save_model(save_path)

    print("\n========================================")
    print(" TRAINING COMPLETE!")
    print(f" Model saved to: {save_path}")
    print("========================================\n")


if __name__ == "__main__":
    train_eurosat()