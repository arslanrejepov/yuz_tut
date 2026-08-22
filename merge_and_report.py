"""
Merge, dedupe, and report on triage JSONL dataset files.

USAGE:
    python merge_and_report.py file1.jsonl file2.jsonl ... -o combined.jsonl

What it does:
1. Loads every input file, tags each row with its source filename
2. Drops exact duplicate `text` values
3. Flags near-duplicates (high char-overlap) for manual review — does NOT
   auto-drop these, since two real patients CAN describe similar symptoms
   similarly; only exact repeats are auto-removed
4. Prints label distribution per field (body_part, urgency, symptom_type)
5. Prints per-source counts, so you can spot if one friend's batch is
   thin, skewed, or dominates the merged set
6. Writes the cleaned, combined file
"""

import json
import sys
import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher

REQUIRED_FIELDS = ["text", "body_part", "urgency", "symptom_type"]


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[SKIP] {path} line {i}: bad JSON ({e})")
                continue
            missing = [k for k in REQUIRED_FIELDS if k not in obj]
            if missing:
                print(f"[SKIP] {path} line {i}: missing fields {missing}")
                continue
            obj["_source"] = path
            rows.append(obj)
    return rows


def find_near_duplicates(rows, threshold=0.9, max_report=30):
    """
    O(n^2) similarity check — fine for a few thousand rows, not for huge sets.
    Only reports pairs, doesn't remove anything automatically.
    """
    flagged = []
    texts = [r["text"] for r in rows]
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if texts[i] == texts[j]:
                continue  # already handled as exact dup
            ratio = SequenceMatcher(None, texts[i], texts[j]).ratio()
            if ratio >= threshold:
                flagged.append((ratio, i, j, texts[i], texts[j]))
    flagged.sort(reverse=True)
    return flagged[:max_report]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="Input JSONL files to merge")
    parser.add_argument("-o", "--output", default="combined_triage_dataset.jsonl")
    parser.add_argument(
        "--near-dup-threshold",
        type=float,
        default=0.9,
        help="Similarity ratio (0-1) above which two texts are flagged as near-dupes",
    )
    args = parser.parse_args()

    all_rows = []
    for path in args.inputs:
        rows = load_jsonl(path)
        print(f"Loaded {len(rows)} valid rows from {path}")
        all_rows.extend(rows)

    print(f"\nTotal rows loaded: {len(all_rows)}")

    # --- exact dedupe on text ---
    seen = set()
    deduped = []
    exact_dupes = 0
    for r in all_rows:
        key = r["text"].strip()
        if key in seen:
            exact_dupes += 1
            continue
        seen.add(key)
        deduped.append(r)

    print(f"Exact duplicate texts removed: {exact_dupes}")
    print(f"Rows after exact dedupe: {len(deduped)}")

    # --- near-duplicate report (manual review only) ---
    near_dupes = find_near_duplicates(deduped, threshold=args.near_dup_threshold)
    if near_dupes:
        print(f"\n[REVIEW] Top near-duplicate pairs (ratio >= {args.near_dup_threshold}):")
        for ratio, i, j, t1, t2 in near_dupes:
            print(f"  {ratio:.2f} | {t1!r}  <->  {t2!r}")
    else:
        print("\nNo near-duplicates found above threshold.")

    # --- label distribution ---
    print("\n=== LABEL DISTRIBUTION ===")
    for field in ["body_part", "urgency", "symptom_type"]:
        counts = Counter(r[field] for r in deduped)
        print(f"\n{field}:")
        for label, count in sorted(counts.items(), key=lambda x: -x[1]):
            flag = "  <-- THIN" if count < 30 else ""
            print(f"  {label:12s} {count:5d}{flag}")

    # --- per-source counts ---
    print("\n=== PER-SOURCE ROW COUNTS ===")
    src_counts = Counter(r["_source"] for r in deduped)
    for src, count in sorted(src_counts.items(), key=lambda x: -x[1]):
        print(f"  {src:40s} {count:5d}")

    # --- critical urgency specific check ---
    critical_rows = [r for r in deduped if r["urgency"] == "critical"]
    print(f"\n=== CRITICAL URGENCY SPOT CHECK ({len(critical_rows)} rows) ===")
    print("First 10 for manual sanity check:")
    for r in critical_rows[:10]:
        print(f"  [{r['_source']}] {r['text']}")

    # --- write combined file (strip internal _source tag by default) ---
    with open(args.output, "w", encoding="utf-8") as f:
        for r in deduped:
            clean = {k: r[k] for k in REQUIRED_FIELDS}
            f.write(json.dumps(clean, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(deduped)} rows to {args.output}")


if __name__ == "__main__":
    main()