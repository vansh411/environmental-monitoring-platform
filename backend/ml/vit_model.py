"""
Vision Transformer for EuroSAT - Minimal Version
Copy this entire file to: backend/ml/vit_model.py
"""

import tensorflow as tf
from tensorflow import keras
import tensorflow_hub as hub
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Union, List, Optional

CLASS_NAMES = [
    "AnnualCrop", "Forest", "HerbaceousVegetation",
    "Highway", "Industrial", "Pasture", "PermanentCrop",
    "Residential", "River", "SeaLake"
]

class ViTModel:
    def __init__(self, num_classes=10, model_path=None):
        self.num_classes = num_classes
        self.image_size = 224
        self.model = None
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self.create_model()
    
    def create_model(self):
        print("🔄 Creating model with pretrained weights...")
        
        inputs = keras.Input(shape=(224, 224, 3))
        vit_url = "https://tfhub.dev/sayakpaul/vit_b16_fe/1"
        vit_layer = hub.KerasLayer(vit_url, trainable=True)
        
        features = vit_layer(inputs)
        x = keras.layers.Dense(512, activation='relu')(features)
        x = keras.layers.Dropout(0.3)(x)
        outputs = keras.layers.Dense(self.num_classes, activation='softmax')(x)
        
        self.model = keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(
            optimizer=keras.optimizers.Adam(1e-4),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print("✅ Model created!")
        return self.model
    
    def preprocess_image(self, image_input):
        if isinstance(image_input, (str, Path)):
            image = Image.open(image_input).convert('RGB')
        elif isinstance(image_input, np.ndarray):
            if image_input.dtype != np.uint8:
                image_input = (image_input * 255).astype(np.uint8)
            image = Image.fromarray(image_input)
        else:
            image = image_input.convert('RGB')
        
        image = image.resize((224, 224))
        image = np.array(image, dtype=np.float32) / 255.0
        
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        return image
    
    def predict(self, image_input, return_probabilities=True):
        if self.model is None:
            raise ValueError("Model not loaded")
        
        image = self.preprocess_image(image_input)
        predictions = self.model.predict(image, verbose=0)
        
        predicted_class = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_class])
        
        result = {
            'predicted_class': predicted_class,
            'predicted_label': CLASS_NAMES[predicted_class],
            'confidence': confidence
        }
        
        if return_probabilities:
            result['probabilities'] = {
                CLASS_NAMES[i]: float(predictions[0][i])
                for i in range(self.num_classes)
            }
        
        return result
    
    def save_model(self, save_path):
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(str(save_path))
        print(f"💾 Model saved to {save_path}")
    
    def load_model(self, model_path):
        print(f"📂 Loading model from {model_path}")
        self.model = keras.models.load_model(str(model_path))
        print("✅ Model loaded!")

class ModelCheckpoint:
    def __init__(self, checkpoint_dir="./models/checkpoints", monitor="val_accuracy"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = monitor
    
    def get_callback(self):
        return keras.callbacks.ModelCheckpoint(
            filepath=str(self.checkpoint_dir / 'best_model.h5'),
            monitor=self.monitor,
            mode='max',
            save_best_only=True,
            verbose=1
        )
    
    def get_callbacks(self):
        return [
            self.get_callback(),
            keras.callbacks.EarlyStopping(monitor=self.monitor, patience=5, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(monitor=self.monitor, factor=0.5, patience=3)
        ]