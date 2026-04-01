"""
backend/ml/vit_model.py
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

# ── Mixed precision: GPU only ──────────────────────────────────────────────────
_gpus = tf.config.list_physical_devices("GPU")
if _gpus:
    try:
        keras.mixed_precision.set_global_policy("mixed_float16")
        print("✓ Mixed precision enabled (GPU detected)")
    except Exception:
        keras.mixed_precision.set_global_policy("float32")
else:
    keras.mixed_precision.set_global_policy("float32")
    print("✓ float32 mode (CPU)")

# ── Constants ──────────────────────────────────────────────────────────────────
CLASS_NAMES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation",
    "Highway", "Industrial", "Pasture", "PermanentCrop",
    "Residential", "River", "SeaLake",
]

VIT_URL = "https://tfhub.dev/sayakpaul/vit_b16_fe/1"


# ── Custom layer ───────────────────────────────────────────────────────────────
class CastToFloat32(keras.layers.Layer):
    """
    Explicit float32 cast before the ViT backbone.
    Using a proper Layer subclass instead of Lambda allows safe_mode loading.
    """
    def call(self, inputs):
        return tf.cast(inputs, tf.float32)

    def get_config(self):
        return super().get_config()


# ── Main model class ───────────────────────────────────────────────────────────
class ViTModel:
    """
    Wraps ViT-B/16 feature extractor from TF-Hub with a classification head.

    Loading behaviour
    -----------------
    weights_path  → build graph first, then load weights-only file (.weights.keras)
    model_path    → load full saved model (architecture + weights together)
    neither       → build a fresh untrained model (used during training)
    """

    def __init__(
        self,
        num_classes: int = 10,
        model_path: Optional[str] = None,
        weights_path: Optional[str] = None,
        freeze_backbone: bool = True,
    ):
        self.num_classes     = num_classes
        self.image_size      = 224
        self.freeze_backbone = freeze_backbone
        self.model           = None

        if weights_path and Path(weights_path).exists():
            # Weights-only checkpoint — must build graph first then load weights
            print(f"  Building graph for weights-only checkpoint...")
            self.create_model()
            self._load_weights_only(weights_path)

        elif model_path and Path(model_path).exists():
            # Full saved model — architecture + weights in one file
            self._load_full_model(model_path)

        else:
            # Fresh model for training
            print("  No existing model found — building fresh model for training.")
            self.create_model()

        # Warmup: one dummy forward pass so first real request is fast
        if self.model is not None:
            self._warmup()

    # ── Graph construction ─────────────────────────────────────────────────────

    def create_model(self):
        mode = "FROZEN backbone" if self.freeze_backbone else "TRAINABLE backbone"
        print(f"  Building ViT-B/16 model ({mode})...")

        inputs    = keras.Input(shape=(self.image_size, self.image_size, 3))
        x         = CastToFloat32(name="cast_to_float32")(inputs)
        vit_layer = hub.KerasLayer(VIT_URL, trainable=not self.freeze_backbone)
        features  = vit_layer(x)
        x         = keras.layers.Dense(256, activation="relu",  name="head_dense")(features)
        x         = keras.layers.Dropout(0.3,                   name="head_dropout")(x)
        outputs   = keras.layers.Dense(
            self.num_classes, activation="softmax",
            dtype="float32", name="predictions"
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
        print(f"  Params — trainable: {trainable:,} / total: {total:,}")
        return self.model

    # ── Loading ────────────────────────────────────────────────────────────────

    def _load_weights_only(self, weights_path: str):
        """
        Load a weights-only checkpoint (.weights.keras or .weights.h5).
        Graph (self.model) must already be built before calling this.
        """
        print(f"  Loading weights from: {weights_path}")
        try:
            self.model.load_weights(str(weights_path))
            print("✓ Weights loaded successfully")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load weights from {weights_path}.\n"
                f"  Error: {e}\n"
                f"  Make sure you trained with the same architecture (ViT-B/16, 10 classes)."
            )

    def _load_full_model(self, model_path: str):
        """
        Load a full saved model (architecture + weights).
        Used when model.save() was called instead of save_weights_only=True.
        """
        print(f"  Loading full saved model from: {model_path}")
        try:
            self.model = keras.models.load_model(
                str(model_path),
                custom_objects={
                    "KerasLayer":     hub.KerasLayer,
                    "CastToFloat32":  CastToFloat32,
                },
                safe_mode=False,
            )
            print("✓ Full model loaded successfully")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model from {model_path}.\n"
                f"  Error: {e}"
            )

    # ── Warmup ─────────────────────────────────────────────────────────────────

    def _warmup(self):
        """
        Run one dummy inference to compile the TF graph before the first
        real request. Prevents a slow first prediction.
        """
        try:
            dummy = np.zeros((1, self.image_size, self.image_size, 3), dtype=np.float32)
            self.model.predict(dummy, verbose=0)
            print("✓ Model warmed up — ready for inference")
        except Exception:
            pass  # warmup failure is non-fatal

    # ── Preprocessing ──────────────────────────────────────────────────────────

    def preprocess_image(self, image_input) -> np.ndarray:
        """
        Accept a file path, numpy array, or PIL Image.
        Returns a (1, 224, 224, 3) float32 array in [0, 1].
        """
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            if image_input.dtype != np.uint8:
                image_input = (image_input * 255).astype(np.uint8)
            image = Image.fromarray(image_input)
        else:
            image = image_input.convert("RGB")

        image = image.resize((self.image_size, self.image_size), Image.BILINEAR)
        arr   = np.array(image, dtype=np.float32) / 255.0
        return np.expand_dims(arr, axis=0)

    # ── Inference ──────────────────────────────────────────────────────────────

    def predict(self, image_input, return_probabilities: bool = True) -> Dict:
        """
        Run inference and return a structured result dict.

        Returns
        -------
        {
            "predicted_class" : "Forest",
            "confidence"      : 0.972,
            "model"           : "ViT-B/16 · EuroSAT",
            "probabilities"   : { "AnnualCrop": 0.01, ... }
        }
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded. Check startup logs for errors.")

        image       = self.preprocess_image(image_input)
        predictions = self.model.predict(image, verbose=0)

        predicted_idx   = int(np.argmax(predictions[0]))
        confidence      = float(predictions[0][predicted_idx])
        predicted_class = CLASS_NAMES[predicted_idx]

        result: Dict = {
            "predicted_class": predicted_class,
            "confidence":      round(confidence, 4),
            "model":           "ViT-B/16 · EuroSAT",
        }

        if return_probabilities:
            result["probabilities"] = {
                CLASS_NAMES[i]: round(float(predictions[0][i]), 4)
                for i in range(self.num_classes)
            }

        return result

    # ── Persistence ────────────────────────────────────────────────────────────

    def save_model(self, save_path: str):
        """Save the full model (architecture + weights) to a .keras file."""
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(str(save_path))
        print(f"✓ Full model saved → {save_path}")

    # ── Fine-tuning helpers ────────────────────────────────────────────────────

    def unfreeze_top_layers(self, num_layers: int = 4, new_lr: float = 5e-5):
        """Unfreeze the top N transformer blocks for phase-2 fine-tuning."""
        backbone           = self.model.layers[2]
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
        print(f"✓ Unfrozen top {num_layers} transformer blocks — LR = {new_lr}")


# ── Checkpoint helper ──────────────────────────────────────────────────────────

class ModelCheckpoint:
    """
    Thin wrapper around Keras callbacks for training.
    Saves weights-only checkpoints in .keras format (Keras 2.12+ default).
    """

    def __init__(
        self,
        checkpoint_dir: str = "./models/checkpoints",
        monitor: str = "val_accuracy",
    ):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor

        # .keras extension — matches what Keras 2.12+ actually writes
        self.weights_file = str(self.checkpoint_dir / "best_model.weights.keras")

    def get_callbacks(self):
        return [
            keras.callbacks.ModelCheckpoint(
                filepath=self.weights_file,
                monitor=self.monitor,
                mode="max",
                save_best_only=True,
                save_weights_only=True,   # keeps file small (~2 MB)
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
