"""
Measures how accurate the FaceNet matching in biometric.py actually is,
using the standard LFW (Labeled Faces in the Wild) "pairs" benchmark instead
of guesswork or a single face.jpg.

WHAT THIS DOES NOT TEST: the Kyber/AES envelope. That's already covered by
test_biometric_crypto.py's round-trip test, which proves the encrypted
embedding decrypts back byte-for-byte. Since AES-GCM is lossless,
wrapping/unwrapping the embedding can't change a match/non-match outcome --
so this script calls DeepFace.represent directly (the same model, "Facenet",
that biometric.py uses) and skips the encrypt/decrypt round trip to avoid
~1000 pointless Kyber keygens.

Records BOTH distance metrics per pair:
  - raw_distance: np.linalg.norm(embedding_a - embedding_b), exactly what
    biometric_decryption() in biometric.py computes today (no normalization).
  - l2_distance: the same, but each embedding is L2-normalized first. This is
    the metric DeepFace's own recommended Facenet threshold (0.8) actually
    assumes -- see analyze_threshold_accuracy.py for why the two give very
    different pictures of the same system's accuracy.

WHY enforce_detection=False: LFW's images are already tightly cropped,
pre-aligned face patches (that's the point of the "funneled" variant). Run
DeepFace's own face detector against a photo that's ALREADY just a face and
it fails to find a "face within the face" -- a dataset artifact, not a bug
in biometric.py's own webcam pipeline where full frames are passed in.

Downloads ~50MB of LFW data on first run (cached by scikit-learn under
~/scikit_learn_data after that).

Run with: py -3.11 collect_lfw_distances.py [--pairs N] [--out FILE]
"""
import argparse
import csv
import os
import time

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import cv2
import numpy as np
from deepface import DeepFace
from sklearn.datasets import fetch_lfw_pairs

MODEL_NAME = "Facenet"  # must match biometric.py's model choice


def to_bgr_uint8(float_rgb_image):
    """sklearn's LFW arrays are float32 RGB in [0, 1]; DeepFace/OpenCV expect
    BGR uint8 in [0, 255]."""
    uint8_rgb = (float_rgb_image * 255).astype(np.uint8)
    return cv2.cvtColor(uint8_rgb, cv2.COLOR_RGB2BGR)


def embed(image_bgr):
    result = DeepFace.represent(
        img_path=image_bgr,
        model_name=MODEL_NAME,
        enforce_detection=False,  # see module docstring
        anti_spoofing=False,      # dataset photos, not a liveness test
    )
    return np.array(result[0]["embedding"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=200,
                         help="how many of the 1000 LFW test pairs to run (default: 200, max 1000)")
    parser.add_argument("--out", default="lfw_distances.csv",
                         help="where to write the resulting distances CSV")
    args = parser.parse_args()

    print("Loading LFW pairs (downloads on first run, cached after)...")
    data = fetch_lfw_pairs(subset="test", color=True, resize=1.0, funneled=True)

    n_pairs = min(args.pairs, len(data.target))
    # data.target_names == ['Different persons', 'Same person']; target==1 is genuine
    indices = np.arange(len(data.target))
    np.random.RandomState(42).shuffle(indices)  # mix genuine/impostor instead of running all 500 genuine first
    indices = indices[:n_pairs]

    rows = []
    start = time.time()
    for done, i in enumerate(indices, start=1):
        img_a = to_bgr_uint8(data.pairs[i][0])
        img_b = to_bgr_uint8(data.pairs[i][1])
        label = "genuine" if data.target[i] == 1 else "impostor"

        try:
            emb_a = embed(img_a)
            emb_b = embed(img_b)
        except Exception as exc:
            print(f"  [{done}/{n_pairs}] pair {i} ({label}): embedding failed, skipping ({exc})")
            continue

        raw_distance = float(np.linalg.norm(emb_a - emb_b))
        emb_a_l2 = emb_a / np.linalg.norm(emb_a)
        emb_b_l2 = emb_b / np.linalg.norm(emb_b)
        l2_distance = float(np.linalg.norm(emb_a_l2 - emb_b_l2))
        rows.append({
            "pair_index": int(i), "label": label,
            "raw_distance": raw_distance, "l2_distance": l2_distance,
        })

        if done % 25 == 0 or done == n_pairs:
            elapsed = time.time() - start
            print(f"  [{done}/{n_pairs}] elapsed {elapsed:.0f}s -- last: {label}, "
                  f"raw={raw_distance:.4f} l2={l2_distance:.4f}")

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["pair_index", "label", "raw_distance", "l2_distance"])
        writer.writeheader()
        writer.writerows(rows)

    genuine = [r["raw_distance"] for r in rows if r["label"] == "genuine"]
    impostor = [r["raw_distance"] for r in rows if r["label"] == "impostor"]
    print(f"\nWrote {len(rows)} distances to {args.out} "
          f"({len(genuine)} genuine, {len(impostor)} impostor)")
    print("Next: py -3.11 analyze_threshold_accuracy.py --in", args.out)


if __name__ == "__main__":
    main()
