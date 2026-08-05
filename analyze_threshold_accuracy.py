"""
Turns raw genuine/impostor distances (from collect_lfw_distances.py) into
concrete accuracy numbers: False Accept Rate (FAR), False Reject Rate (FRR),
and the Equal Error Rate (EER) threshold, swept across candidate thresholds.

Two threshold shapes are evaluated side by side:
  - "single-sided": distance < T  (DeepFace's own recommended shape for
    Facenet + euclidean_l2, and what PROJECT_STATUS.md proposes as the fix)
  - "band" (current app behavior): 0.6 <= distance <= T, matching the
    biometric_decryption() logic in biometric.py today

Use --metric to pick which distance column to analyze:
  - raw (default): np.linalg.norm(embedding_a - embedding_b) with NO
    normalization -- exactly what biometric.py computes today.
  - l2: embeddings L2-normalized before the distance, which is the metric
    DeepFace's 0.8 Facenet threshold actually assumes. Comparing the two
    tells you whether 0.6-0.8 is merely mistuned or fundamentally the wrong
    metric for what biometric.py currently computes.

This is read-only analysis over already-collected data -- no webcam, no
DeepFace, no dataset download. Re-run freely while tuning.

Run with: py -3.11 analyze_threshold_accuracy.py [--in lfw_distances.csv] [--metric raw|l2]
"""
import argparse
import csv

CURRENT_APP_BAND_LOW = 0.6  # biometric.py's hardcoded lower bound


def load_distances(path, metric):
    column = "raw_distance" if metric == "raw" else "l2_distance"
    genuine, impostor = [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            bucket = genuine if row["label"] == "genuine" else impostor
            bucket.append(float(row[column]))
    return genuine, impostor


def rate(distances, predicate):
    if not distances:
        return float("nan")
    return sum(1 for d in distances if predicate(d)) / len(distances)


def build_thresholds(all_distances):
    """Spans the actual observed data range (so the sweep is meaningful for
    both raw and l2 distance scales) while always including 0.6 and 0.8 --
    biometric.py's literal hardcoded constants -- even if they fall outside
    that range, since 'the real threshold never matches real distances' is
    itself the finding for the raw metric."""
    lo, hi = min(all_distances), max(all_distances)
    span = (hi - lo) or 1.0
    steps = 14
    generated = [lo + span * i / steps for i in range(steps + 1)]
    return sorted(set(round(t, 3) for t in generated + [0.6, 0.8]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="in_path", default="lfw_distances.csv")
    parser.add_argument("--metric", choices=["raw", "l2"], default="raw",
                         help="raw = exactly what biometric.py computes today (default); "
                              "l2 = L2-normalize embeddings first, the metric the 0.8 threshold assumes")
    args = parser.parse_args()

    genuine, impostor = load_distances(args.in_path, args.metric)
    if not genuine or not impostor:
        raise SystemExit(
            f"Need both genuine and impostor distances in {args.in_path} -- "
            f"got {len(genuine)} genuine, {len(impostor)} impostor. "
            f"Run collect_lfw_distances.py first (with enough --pairs to hit both)."
        )

    print(f"Metric: {args.metric}")
    print(f"Loaded {len(genuine)} genuine + {len(impostor)} impostor distances from {args.in_path}\n")
    print(f"genuine distance:  min={min(genuine):.4f}  max={max(genuine):.4f}  "
          f"mean={sum(genuine)/len(genuine):.4f}")
    print(f"impostor distance: min={min(impostor):.4f}  max={max(impostor):.4f}  "
          f"mean={sum(impostor)/len(impostor):.4f}\n")

    thresholds = build_thresholds(genuine + impostor)

    header = f"{'threshold':>9} | {'single FAR':>10} {'single FRR':>10} | {'band FAR':>9} {'band FRR':>9}"
    print(header)
    print("-" * len(header))

    best_single = min(
        thresholds,
        key=lambda t: abs(rate(impostor, lambda d: d < t) - rate(genuine, lambda d: d >= t)),
    )

    for t in thresholds:
        single_far = rate(impostor, lambda d: d < t)   # impostor wrongly accepted
        single_frr = rate(genuine, lambda d: d >= t)   # genuine wrongly rejected

        band_far = rate(impostor, lambda d: CURRENT_APP_BAND_LOW <= d <= t)
        band_frr = rate(genuine, lambda d: not (CURRENT_APP_BAND_LOW <= d <= t))

        markers = []
        if t == best_single:
            markers.append("~EER")
        if t == 0.8:
            markers.append("current app threshold (0.8)")
        if t == 0.6:
            markers.append("current app band floor (0.6)")
        marker = ("  <-- " + ", ".join(markers)) if markers else ""
        print(f"{t:>9.3f} | {single_far:>10.1%} {single_frr:>10.1%} | "
              f"{band_far:>9.1%} {band_frr:>9.1%}{marker}")

    print(
        "\nsingle-sided = 'distance < T' (DeepFace's recommended shape). "
        "band = current biometric.py logic '0.6 <= distance <= T'.\n"
        "FAR = fraction of impostor pairs wrongly accepted (security risk).\n"
        "FRR = fraction of genuine pairs wrongly rejected (usability cost).\n"
        "EER row is where FAR and FRR are closest -- a reasonable threshold "
        "candidate, not necessarily the best choice if you'd rather bias "
        "toward fewer false accepts than false rejects."
    )


if __name__ == "__main__":
    main()
