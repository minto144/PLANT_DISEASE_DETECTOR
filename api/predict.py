"""
predict.py — Load the trained model and run inference.
"""

import os
import json
import numpy as np
from PIL import Image
import io
import tensorflow as tf

from .classes import get_disease_info, CLASS_LABELS

# Works both locally and on Render
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH     = os.path.join(BASE_DIR, "model", "saved_model", "plant_disease_model.keras")
CLASS_MAP_PATH = os.path.join(BASE_DIR, "model", "saved_model", "class_indices.json")
IMG_SIZE       = (224, 224)

_model        = None
_idx_to_class = None


def load_model():
    global _model, _idx_to_class
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Train it first: python model/train.py"
            )
        print(f"📥 Loading model from {MODEL_PATH}...")
        _model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ Model loaded.")
    if _idx_to_class is None:
        if os.path.exists(CLASS_MAP_PATH):
            with open(CLASS_MAP_PATH) as f:
                class_indices = json.load(f)
            _idx_to_class = {v: k for k, v in class_indices.items()}
        else:
            _idx_to_class = {i: label for i, label in enumerate(CLASS_LABELS)}
    return _model, _idx_to_class


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)


def predict(image_bytes: bytes, top_k: int = 3) -> dict:
    model, idx_to_class = load_model()
    arr   = preprocess_image(image_bytes)
    preds = model.predict(arr, verbose=0)[0]
    top_indices = np.argsort(preds)[::-1][:top_k]
    results = []
    for idx in top_indices:
        label      = idx_to_class.get(int(idx), CLASS_LABELS[int(idx)])
        confidence = float(preds[idx])
        info       = get_disease_info(label)
        results.append({"class_label": label, "confidence": round(confidence * 100, 2), **info})
    return {"top_prediction": results[0], "alternatives": results[1:]}
