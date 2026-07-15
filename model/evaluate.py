"""
evaluate.py — Evaluate the trained model.
Generates accuracy metrics, confusion matrix, and classification report.

Run from project root:
    python model/evaluate.py
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix

DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset", "PlantVillage")
MODEL_PATH  = os.path.join(os.path.dirname(__file__), "saved_model", "plant_disease_model.keras")
CLASS_MAP   = os.path.join(os.path.dirname(__file__), "saved_model", "class_indices.json")
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32


def evaluate():
    print("📥 Loading model...")
    model = tf.keras.models.load_model(MODEL_PATH)

    with open(CLASS_MAP) as f:
        class_indices = json.load(f)
    idx_to_class = {v: k for k, v in class_indices.items()}

    datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)
    val_gen = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
    )

    print("🔍 Running predictions...")
    preds = model.predict(val_gen, verbose=1)
    y_pred = np.argmax(preds, axis=1)
    y_true = val_gen.classes

    class_names = [idx_to_class[i] for i in range(len(idx_to_class))]

    print("\n📊 Classification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Confusion matrix (top 15 classes for readability)
    cm = confusion_matrix(y_true, y_pred)
    top_n = min(15, len(class_names))
    top_indices = np.argsort(np.sum(cm, axis=1))[-top_n:]
    cm_top = cm[np.ix_(top_indices, top_indices)]
    top_names = [class_names[i] for i in top_indices]

    plt.figure(figsize=(14, 10))
    sns.heatmap(cm_top, annot=True, fmt="d", cmap="Greens",
                xticklabels=top_names, yticklabels=top_names)
    plt.title("Confusion Matrix (top classes)")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), "saved_model", "confusion_matrix.png")
    plt.savefig(out_path, dpi=120)
    print(f"\n📸 Confusion matrix saved → {out_path}")


if __name__ == "__main__":
    evaluate()