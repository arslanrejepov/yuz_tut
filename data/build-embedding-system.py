import json

INPUT_JSONL = "locations_merged.jsonl"
OUTPUT_JSONL = "locations_embedding_ready.jsonl"

BODY_MAX_CHARS = 300


def build_embedding_text(rec):
    parts = []

    parts.append(rec["name_tm"])

    if rec["categories"]:
        parts.append(", ".join(rec["categories"]))

    if rec["address_tm"]:
        parts.append(rec["address_tm"])

    if rec["seo_keywords"]:
        parts.append(rec["seo_keywords"])

    if rec["body_tm"]:
        body = rec["body_tm"][:BODY_MAX_CHARS]
        parts.append(body)

    return " | ".join(p.strip() for p in parts if p and p.strip())


def build_metadata(rec):
    return {
        "id": rec["id"],
        "name_tm": rec["name_tm"],
        "address_tm": rec["address_tm"],
        "categories": rec["categories"],
        "latitude": rec["latitude"],
        "longitude": rec["longitude"],
        "has_location": rec["latitude"] is not None and rec["longitude"] is not None,
        "star": rec["star"],
        "review_count": rec["review_count"],
        "is_open": rec["is_open"],
        "round_the_clock": rec["round_the_clock"],
        "hours": rec["hours"],
        "contacts": rec["contacts"],
        "slug": rec["slug"],
    }


def main():
    count = 0
    empty_text = 0

    with open(INPUT_JSONL, encoding="utf-8") as fin, \
         open(OUTPUT_JSONL, "w", encoding="utf-8") as fout:
        for line in fin:
            rec = json.loads(line)
            text = build_embedding_text(rec)
            if not text:
                empty_text += 1
                continue

            out_rec = {
                "id": rec["id"],
                "embedding_text": text,
                "metadata": build_metadata(rec),
            }
            fout.write(json.dumps(out_rec, ensure_ascii=False) + "\n")
            count += 1

    print(f"records written:     {count}")
    print(f"skipped (empty text): {empty_text}")
    print(f"output: {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()