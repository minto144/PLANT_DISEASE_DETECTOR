"""
train.py — Plant Disease Detection Model Training
Uses MobileNetV2 with transfer learning on the PlantVillage dataset.

Run from project root:
    python model/train.py
"""


import os
import json
import numpy as np
import tensorflow as tf
import keras
from keras import layers, Model, Input
from keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
)

# ─── Config ───────────────────────────────────────────────────────────────────

DATASET_DIR   = os.path.join(os.path.dirname(__file__), "..", "dataset", "PlantVillage")
MODEL_DIR     = os.path.join(os.path.dirname(__file__), "saved_model")
IMG_SIZE      = (224, 224)
BATCH_SIZE    = 32
EPOCHS_WARMUP = 15    # Phase 1: head only — needs enough epochs to converge
EPOCHS_FINE   = 25    # Phase 2: fine-tune top base layers
LR_WARMUP     = 1e-3  # Higher LR for warmup (head learns from scratch)
LR_FINETUNE   = 1e-4  # Lower LR for fine-tuning (avoid destroying pretrained weights)
VAL_SPLIT     = 0.2
SEED          = 42

os.makedirs(MODEL_DIR, exist_ok=True)

# ─── Data Generators ──────────────────────────────────────────────────────────

def build_generators(dataset_dir):
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=VAL_SPLIT,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.2,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode="nearest",
    )
    val_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=VAL_SPLIT,
    )

    train_gen = train_datagen.flow_from_directory(
        dataset_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        seed=SEED,
        shuffle=True,
    )
    val_gen = val_datagen.flow_from_directory(
        dataset_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        seed=SEED,
        shuffle=False,
    )
    return train_gen, val_gen


# ─── Model ────────────────────────────────────────────────────────────────────

def build_model(num_classes: int):
    base = MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # Freeze entire base during Phase 1

    inputs = Input(shape=(*IMG_SIZE, 3))
    # training=False is critical: keeps BatchNorm layers in base frozen
    x = base(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = Model(inputs, outputs)
    return model, base


# ─── Training ─────────────────────────────────────────────────────────────────

def train():
    print("\n📦 Loading dataset...")
    train_gen, val_gen = build_generators(DATASET_DIR)
    num_classes = len(train_gen.class_indices)
    print(f"   Classes : {num_classes}")
    print(f"   Training: {train_gen.samples} images")
    print(f"   Validation: {val_gen.samples} images")

    # Save class index → label mapping (used by the API)
    class_map_path = os.path.join(MODEL_DIR, "class_indices.json")
    with open(class_map_path, "w") as f:
        json.dump(train_gen.class_indices, f, indent=2)
    print(f"   ✅ Class map saved → {class_map_path}")

    print("\n🏗  Building model (MobileNetV2 + custom head)...")
    model, base = build_model(num_classes)
    model.summary()

    # ── Phase 1: Warmup ───────────────────────────────────────────────────────
    # Base is fully frozen. Only the custom head trains.
    # Must reach ~85-95% val_accuracy before moving to Phase 2.
    print(f"\n{'='*55}")
    print(f"🔒 PHASE 1 — Warmup: training head only")
    print(f"   Epochs: {EPOCHS_WARMUP}  |  LR: {LR_WARMUP}")
    print(f"   Target: val_accuracy > 85% before Phase 2")
    print(f"{'='*55}")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR_WARMUP),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_p1 = [
        ModelCheckpoint(
            os.path.join(MODEL_DIR, "best_phase1.keras"),
            save_best_only=True,
            monitor="val_accuracy",
            verbose=1,
        ),
        EarlyStopping(
            patience=5,
            restore_best_weights=True,
            monitor="val_accuracy",
            verbose=1,
        ),
    ]

    history_p1 = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_WARMUP,
        callbacks=callbacks_p1,
    )

    best_p1_acc = max(history_p1.history["val_accuracy"])
    print(f"\n✅ Phase 1 complete — best val accuracy: {best_p1_acc:.4f} ({best_p1_acc*100:.1f}%)")

    if best_p1_acc < 0.5:
        print("\n⚠️  WARNING: val accuracy is very low after warmup.")
        print("   Possible causes:")
        print("   1. Dataset folder structure is wrong.")
        print("      Expected: dataset/PlantVillage/<ClassName>/<image.jpg>")
        print("   2. Too few images per class.")
        print("   Stopping before fine-tuning to avoid wasting time.")
        return

    # ── Phase 2: Fine-tuning ──────────────────────────────────────────────────
    # Unfreeze top 50 layers of base. Use a much lower LR.
    print(f"\n{'='*55}")
    print(f"🔓 PHASE 2 — Fine-tuning top 50 base layers")
    print(f"   Epochs: {EPOCHS_FINE}  |  LR: {LR_FINETUNE}")
    print(f"{'='*55}")

    base.trainable = True
    for layer in base.layers[:-50]:
        layer.trainable = False

    trainable_count = sum(1 for l in base.layers if l.trainable)
    print(f"   Unfrozen base layers: {trainable_count}")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(LR_FINETUNE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    callbacks_p2 = [
        ModelCheckpoint(
            os.path.join(MODEL_DIR, "plant_disease_model.keras"),
            save_best_only=True,
            monitor="val_accuracy",
            verbose=1,
        ),
        EarlyStopping(
            patience=7,
            restore_best_weights=True,
            monitor="val_accuracy",
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1,
        ),
    ]

    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS_FINE,
        callbacks=callbacks_p2,
    )

    # ── Final evaluation ──────────────────────────────────────────────────────
    print("\n📊 Running final evaluation on validation set...")
    loss, acc = model.evaluate(val_gen, verbose=1)
    print(f"\n{'='*55}")
    print(f"✅ TRAINING COMPLETE")
    print(f"   Final val accuracy : {acc*100:.2f}%")
    print(f"   Final val loss     : {loss:.4f}")
    print(f"   Model saved to     : {MODEL_DIR}/plant_disease_model.keras")
    print(f"{'='*55}")


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🌿 Plant Disease Detection — Model Training")
    print("=" * 55)
    print(f"   TensorFlow version : {tf.__version__}")
    print(f"   Dataset dir        : {os.path.abspath(DATASET_DIR)}")
    print(f"   Model output dir   : {os.path.abspath(MODEL_DIR)}")

    if not os.path.exists(DATASET_DIR):
        print(f"\n❌ Dataset not found at: {DATASET_DIR}")
        print("   1. Go to: https://www.kaggle.com/datasets/emmarex/plantdisease")
        print("   2. Download and unzip")
        print("   3. Place at: dataset/PlantVillage/")
        exit(1)

    # Quick sanity check on dataset structure
    subdirs = [d for d in os.listdir(DATASET_DIR)
               if os.path.isdir(os.path.join(DATASET_DIR, d))]
    if len(subdirs) < 2:
        print(f"\n❌ Dataset structure looks wrong.")
        print(f"   Found only {len(subdirs)} subfolder(s) in {DATASET_DIR}")
        print("   Each subfolder should be a disease class with images inside.")
        exit(1)

    print(f"\n   Found {len(subdirs)} class folders ✅")
    train()