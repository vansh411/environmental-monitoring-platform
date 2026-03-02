"""
Vision Transformer for EuroSAT
Copy to: backend/ml/vit_model.py
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
_gpus = tf.config.list_physical_devices("GPU")
if _gpus:
    try:
        keras.mixed_precision.set_global_policy("mixed_float16")
        print("✓ Mixed precision enabled (GPU detected)")
    except Exception as e:
        keras.mixed_precision.set_global_policy("float32")
else:
    keras.mixed_precision.set_global_policy("float32")
    print("✓ float32 mode (CPU)")

CLASS_NAMES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation",
    "Highway", "Industrial", "Pasture", "PermanentCrop",
    "Residential", "River", "SeaLake"
]

VIT_URL = "https://tfhub.dev/sayakpaul/vit_b16_fe/1"


class CastToFloat32(keras.layers.Layer):
    """Replaces Lambda layer — serializes safely without safe_mode issues."""
    def call(self, inputs):
        return tf.cast(inputs, tf.float32)
    def get_config(self):
        return super().get_config()


class ViTModel:
    def __init__(
        self,
        num_classes: int = 10,
        model_path: Optional[str] = None,
        weights_path: Optional[str] = None,   # ← NEW: explicit weights-only loading
        freeze_backbone: bool = True,
    ):
        self.num_classes = num_classes
        self.image_size = 224
        self.freeze_backbone = freeze_backbone
        self.model = None

        if model_path and Path(model_path).exists():
            # Full saved model — architecture + weights together
            self._load_full_model(model_path)
        elif weights_path and Path(weights_path).exists():
            # Weights-only — build graph first then load weights
            self.create_model()
            self._load_weights_only(weights_path)
        else:
            # Fresh model — build from scratch
            self.create_model()

    # ─────────────────────────────────────────────────────────────────────────
    def create_model(self):
        mode = "FROZEN" if self.freeze_backbone else "TRAINABLE"
        print(f"✓ Building ViT model ({mode} backbone)...")

        inputs = keras.Input(shape=(self.image_size, self.image_size, 3))
        x = CastToFloat32(name="cast_to_float32")(inputs)
        vit_layer = hub.KerasLayer(VIT_URL, trainable=not self.freeze_backbone)
        features = vit_layer(x)
        x = keras.layers.Dense(256, activation="relu", name="head_dense")(features)
        x = keras.layers.Dropout(0.3, name="head_dropout")(x)
        outputs = keras.layers.Dense(
            self.num_classes, activation="softmax", dtype="float32", name="predictions"
        )(x)

        self.model = keras.Model(inputs=inputs, outputs=outputs)
        lr = 1e-3 if self.freeze_backbone else 1e-4
        self.model.compile(
            optimizer=keras.optimizers.Adam(lr),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        trainable = sum(tf.size(v).numpy() for v in self.model.trainable_variables)
        total     = sum(tf.size(v).numpy() for v in self.model.variables)
        print(f"✓ Model built — trainable params: {trainable:,} / {total:,}")
        return self.model

    # ─────────────────────────────────────────────────────────────────────────
    def _load_full_model(self, model_path: str):
        """Load a complete saved model (architecture + weights)."""
        print(f"✓ Loading full model from: {model_path}")
        self.model = keras.models.load_model(
            str(model_path),
            custom_objects={
                "KerasLayer": hub.KerasLayer,
                "CastToFloat32": CastToFloat32,
            },
            safe_mode=False,
        )
        print("✓ Full model loaded!")

    def _load_weights_only(self, weights_path: str):
        """Load weights into an already-built model graph."""
        print(f"✓ Loading weights from: {weights_path}")
        self.model.load_weights(str(weights_path))
        print("✓ Weights loaded!")

    # ── Keep load_model for backwards compatibility ───────────────────────────
    def load_model(self, model_path: str):
        self._load_full_model(model_path)

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

    def unfreeze_top_layers(self, num_layers: int = 4, new_lr: float = 5e-5):
        backbone = self.model.layers[2]
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


# ─────────────────────────────────────────────────────────────────────────────
class ModelCheckpoint:
    def __init__(self, checkpoint_dir="./models/checkpoints", monitor="val_accuracy"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor

    def get_callbacks(self):
        return [
            keras.callbacks.ModelCheckpoint(
                filepath=str(self.checkpoint_dir / "best_model.weights.h5"),
                monitor=self.monitor,
                mode="max",
                save_best_only=True,
                save_weights_only=True,
                verbose=1,
            ),
            keras.callbacks.EarlyStopping(
                monitor=self.monitor,
                patience=3,
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
