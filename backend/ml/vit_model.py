"""
Vision Transformer for EuroSAT - Optimized Version
Copy this entire file to: backend/ml/vit_model.py

Key optimizations:
  1. ViT backbone is FROZEN by default — only the classification head trains (~10x faster)
  2. Mixed precision is ONLY enabled on GPU — TFHub ViT strictly requires float32 inputs,
     so mixed_float16 on CPU caused the "dtype=float16" ValueError you saw.
  3. Explicit float32 cast before the ViT layer as a hard safety net.
  4. TFHub weights cached locally — no re-download on subsequent runs.
"""

import os
os.environ.setdefault("TFHUB_CACHE_DIR", "./models/tfhub_cache")

import tensorflow as tf
from tensorflow import keras
import tensorflow_hub as hub
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Optional

# ── Mixed precision: GPU only ─────────────────────────────────────────────────
# Root cause of your error: mixed_float16 was casting inputs to float16,
# but the TFHub SavedModel only has a concrete function for float32 inputs.
# On CPU mixed precision gives zero benefit anyway, so we simply don't enable it.
_gpus = tf.config.list_physical_devices("GPU")
if _gpus:
    try:
        keras.mixed_precision.set_global_policy("mixed_float16")
        print("✓ Mixed precision enabled (GPU detected)")
    except Exception as e:
        print(f"⚠ Mixed precision unavailable: {e}")
        keras.mixed_precision.set_global_policy("float32")
else:
    keras.mixed_precision.set_global_policy("float32")
    print("✓ float32 mode (CPU — mixed precision skipped)")

CLASS_NAMES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation",
    "Highway", "Industrial", "Pasture", "PermanentCrop",
    "Residential", "River", "SeaLake"
]

VIT_URL = "https://tfhub.dev/sayakpaul/vit_b16_fe/1"


class ViTModel:
    def __init__(
        self,
        num_classes: int = 10,
        model_path: Optional[str] = None,
        freeze_backbone: bool = True,
    ):
        self.num_classes = num_classes
        self.image_size = 224
        self.freeze_backbone = freeze_backbone
        self.model = None

        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self.create_model()

    # ─────────────────────────────────────────────────────────────────────────
    def create_model(self):
        mode = "FROZEN backbone (head-only)" if self.freeze_backbone else "FULL fine-tune"
        print(f"✓ Creating ViT model — {mode}")

        inputs = keras.Input(shape=(self.image_size, self.image_size, 3))

        # ── Critical fix: explicitly cast to float32 before entering the ViT ──
        # The TFHub SavedModel only has a concrete function for float32 tensors.
        # If mixed precision is ever re-enabled, this cast prevents the dtype crash.
        x = keras.layers.Lambda(
            lambda t: tf.cast(t, tf.float32),
            name="force_float32"
        )(inputs)

        # Frozen backbone: 86M params locked, only head trains
        vit_layer = hub.KerasLayer(VIT_URL, trainable=not self.freeze_backbone)
        features = vit_layer(x)  # shape: (batch, 768), always float32

        # Lightweight classification head
        x = keras.layers.Dense(256, activation="relu", name="head_dense")(features)
        x = keras.layers.Dropout(0.3, name="head_dropout")(x)
        outputs = keras.layers.Dense(
            self.num_classes, activation="softmax", dtype="float32", name="predictions"
        )(x)

        self.model = keras.Model(inputs=inputs, outputs=outputs)

        # Higher LR is fine when only the small head is training
        lr = 1e-3 if self.freeze_backbone else 1e-4
        self.model.compile(
            optimizer=keras.optimizers.Adam(lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        trainable = sum(tf.size(v).numpy() for v in self.model.trainable_variables)
        total     = sum(tf.size(v).numpy() for v in self.model.variables)
        print(f"✓ Trainable params: {trainable:,} / {total:,} total")
        return self.model

    # ─────────────────────────────────────────────────────────────────────────
    def unfreeze_top_layers(self, num_layers: int = 4, new_lr: float = 5e-5):
        """Phase-2 fine-tuning — GPU only. Unfreezes top N transformer blocks."""
        backbone = self.model.layers[2]  # index 2 now because Lambda is layer 1
        backbone.trainable = True

        block_cutoff = 12 - num_layers
        for var in backbone.trainable_variables:
            block_nums = [
                int(s.replace("encoderblock_", ""))
                for s in var.name.split("/")
                if "encoderblock_" in s
            ]
            if block_nums and block_nums[0] < block_cutoff:
                var._trainable = False

        self.model.compile(
            optimizer=keras.optimizers.Adam(new_lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        print(f"✓ Unfrozen top {num_layers} transformer blocks — LR={new_lr}")

    # ─────────────────────────────────────────────────────────────────────────
    def preprocess_image(self, image_input):
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            if image_input.dtype != np.uint8:
                image_input = (image_input * 255).astype(np.uint8)
            image = Image.fromarray(image_input)
        else:
            image = image_input.convert("RGB")

        image = image.resize((self.image_size, self.image_size))
        image = np.array(image, dtype=np.float32) / 255.0
        return np.expand_dims(image, axis=0)

    # ─────────────────────────────────────────────────────────────────────────
    def predict(self, image_input, return_probabilities: bool = True) -> Dict:
        if self.model is None:
            raise ValueError("Model not loaded")

        image = self.preprocess_image(image_input)
        predictions = self.model.predict(image, verbose=0)

        predicted_class = int(np.argmax(predictions[0]))
        confidence      = float(predictions[0][predicted_class])

        result = {
            "predicted_class": CLASS_NAMES[predicted_class],
            "confidence": confidence,
            "model": "ViT-B/16 · EuroSAT",
        }

        if return_probabilities:
            result["probabilities"] = {
                CLASS_NAMES[i]: float(predictions[0][i])
                for i in range(self.num_classes)
            }

        return result

    # ─────────────────────────────────────────────────────────────────────────
    def save_model(self, save_path: str):
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(str(save_path))
        print(f"✓ Model saved → {save_path}")

    def load_model(self, model_path: str):
        print(f"✓ Loading model from {model_path}")
        self.model = keras.models.load_model(
            str(model_path),
            custom_objects={"KerasLayer": hub.KerasLayer},
        )
        print("✓ Model loaded!")


# ─────────────────────────────────────────────────────────────────────────────
class ModelCheckpoint:
    def __init__(self, checkpoint_dir="./models/checkpoints", monitor="val_accuracy"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor

    def get_callbacks(self):
        return [
            keras.callbacks.ModelCheckpoint(
                filepath=str(self.checkpoint_dir / "best_model.keras"),
                monitor=self.monitor,
                mode="max",
                save_best_only=True,
                verbose=1,
            ),
            keras.callbacks.EarlyStopping(
                monitor=self.monitor,
                patience=4,
                restore_best_weights=True,
                verbose=1,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor=self.monitor,
                factor=0.5,
                patience=2,
                min_lr=1e-6,
                verbose=1,
            ),
        ]
