"""
train_model.py — Optimized for slow CPU systems

Settings tuned for your machine:
  - Batch size 16    → less memory pressure, still fast
  - Subset 30%       → ~400 batches per epoch instead of 1350
  - Max 3 epochs     → early stopping kicks in around epoch 2-3
  - No augmentation  → saves CPU time per batch

  Estimated time : 20-35 minutes total (CPU)
  Expected accuracy: 85-90%

NOTE: For faster + better training, use GeoSentinel_Colab_Training.py on Colab GPU.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import tensorflow as tf
from backend.ml.vit_model import ViTModel, ModelCheckpoint

# ─── Config ───────────────────────────────────────────────────────────────────
DATASET_PATH    = Path("data/eurosat/EuroSAT")
IMAGE_SIZE      = (224, 224)
AUTOTUNE        = tf.data.AUTOTUNE
GPU_AVAILABLE   = bool(tf.config.list_physical_devices("GPU"))

BATCH_SIZE      = 32 if GPU_AVAILABLE else 16
SUBSET_FRACTION = 0.3
PHASE1_EPOCHS   = 3

print(f"\n{'GPU' if GPU_AVAILABLE else 'CPU'} detected")
print(f"Batch size     : {BATCH_SIZE}")
print(f"Subset         : {int(SUBSET_FRACTION * 100)}% of dataset")
print(f"Max epochs     : {PHASE1_EPOCHS}\n")


# ─── Dataset ──────────────────────────────────────────────────────────────────
def load_eurosat_dataset():
    print(f"Loading EuroSAT from: {DATASET_PATH}")

    common_kwargs = dict(
        labels="inferred",
        label_mode="int",
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        seed=42,
        validation_split=0.2,
    )

    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_PATH, subset="training", shuffle=True, **common_kwargs
    )
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        DATASET_PATH, subset="validation", shuffle=False, **common_kwargs
    )

    train_card = train_ds.cardinality().numpy()
    val_card   = val_ds.cardinality().numpy()

    if train_card > 0:
        take_train = max(1, int(train_card * SUBSET_FRACTION))
        take_val   = max(1, int(val_card   * SUBSET_FRACTION))
    else:
        take_train = int(1350 * SUBSET_FRACTION)
        take_val   = int(337  * SUBSET_FRACTION)

    print(f"Using {take_train} train batches, {take_val} val batches per epoch")

    def normalize(image, label):
        return tf.cast(image, tf.float32) / 255.0, label

    train_ds = (
        train_ds
        .take(take_train)
        .map(normalize, num_parallel_calls=AUTOTUNE)
        .cache()
        .prefetch(AUTOTUNE)
    )
    val_ds = (
        val_ds
        .take(take_val)
        .map(normalize, num_parallel_calls=AUTOTUNE)
        .cache()
        .prefetch(AUTOTUNE)
    )

    print("✓ Dataset ready\n")
    return train_ds, val_ds


# ─── Training ─────────────────────────────────────────────────────────────────
def train_eurosat():
    print("=" * 52)
    print("  TRAINING VISION TRANSFORMER ON EUROSAT")
    print("=" * 52 + "\n")

    train_ds, val_ds = load_eurosat_dataset()
    checkpoint = ModelCheckpoint()

    print("── Phase 1: Head-only training ──────────────────────")
    print("   Backbone frozen — only ~200K params train")
    print(f"  Checkpoint → {checkpoint.weights_file}\n")

    vit = ViTModel(num_classes=10, freeze_backbone=True)

    history = vit.model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE1_EPOCHS,
        callbacks=checkpoint.get_callbacks(),
        verbose=1,
    )

    best_acc   = max(history.history.get("val_accuracy", [0]))
    epochs_run = len(history.history["val_accuracy"])

    print(f"\n✓ Training complete")
    print(f"  Epochs run        : {epochs_run} / {PHASE1_EPOCHS}")
    print(f"  Best val accuracy : {best_acc * 100:.1f}%")
    print(f"  Weights saved to  : {checkpoint.weights_file}")

    if not GPU_AVAILABLE:
        print("  Phase 2 skipped   : no GPU")

    print("\n" + "=" * 52)
    print("  DONE! Start the backend with:")
    print("  python -m uvicorn backend.main:app --reload --port 8000")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    for gpu in tf.config.list_physical_devices("GPU"):
        tf.config.experimental.set_memory_growth(gpu, True)
    train_eurosat()
