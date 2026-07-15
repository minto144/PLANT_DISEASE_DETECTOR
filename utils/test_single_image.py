"""
utils/test_single_image.py — Quick CLI tool to test the model on one image.

Usage:
    python utils/test_single_image.py path/to/leaf.jpg
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from predict import predict


def main():
    if len(sys.argv) < 2:
        print("Usage: python utils/test_single_image.py <image_path>")
        sys.exit(1)

    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"❌ File not found: {img_path}")
        sys.exit(1)

    print(f"\n🔬 Analyzing: {img_path}\n")

    with open(img_path, "rb") as f:
        image_bytes = f.read()

    result = predict(image_bytes, top_k=3)
    top = result["top_prediction"]

    print("=" * 55)
    print(f"  Plant      : {top['plant']}")
    print(f"  Disease    : {top['name']}")
    print(f"  Confidence : {top['confidence']}%")
    print(f"  Severity   : {top['severity'].upper()}")
    print(f"\n  Symptoms   : {top['symptoms']}")
    print(f"  Treatment  : {top['treatment']}")
    print(f"  Prevention : {top['prevention']}")
    print("=" * 55)

    if result["alternatives"]:
        print("\nOther possibilities:")
        for alt in result["alternatives"]:
            print(f"  • {alt['name']} ({alt['plant']}) — {alt['confidence']}%")
    print()


if __name__ == "__main__":
    main()