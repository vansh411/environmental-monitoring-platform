"""
Test script - Copy to: test_model.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.ml.vit_model import ViTModel
import numpy as np

print("\n" + "="*70)
print("🧪 TESTING VISION TRANSFORMER")
print("="*70)

# Test 1: Create model
print("\nTest 1: Creating model...")
vit = ViTModel(num_classes=10)
print("✅ Model created!")

# Test 2: Predict
print("\nTest 2: Testing prediction...")
dummy_image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
result = vit.predict(dummy_image)

print(f"🎯 Predicted: {result['predicted_label']}")
print(f"   Confidence: {result['confidence']:.2%}")
print("✅ Prediction works!")

# Test 3: Save/Load
print("\nTest 3: Testing save/load...")
vit.save_model("./models/test_model.h5")
vit_loaded = ViTModel(model_path="./models/test_model.h5")
print("✅ Save/load works!")

print("\n" + "="*70)
print("🎉 ALL TESTS PASSED!")
print("="*70 + "\n")