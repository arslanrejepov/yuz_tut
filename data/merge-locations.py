import json
import re
import sys
import zipfile
from pathlib import Path
from html import unescape

INPUT_DIR = "sections"                # e.g. "extracted_data" if you already unzipped
OUTPUT_JSONL = "locations_merged.jsonl"

TAG_RE = re.compile(r"<[^>]+>")


def clean_html(text):
    if not text:
        return ""
    text = unescape(text)
    text = TAG_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def iter_json_files_from_zip(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.endswith(".json"):
                with z.open(name) as f:
                    try:
                        yield name, json.load(f)
                    except json.JSONDecodeError:
                        print(f"SKIP (bad json): {name}", file=sys.stderr)


def iter_json_files_from_dir(dir_path):
    for path in Path(dir_path).rglob("*.json"):
        try:
            yield str(path), json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"SKIP (bad json): {path}", file=sys.stderr)


def normalize_detail(d):
    hours = d.get("hours") or {}
    contacts = [
        {"name_tm": c.get("name_tm"), "value": c.get("value")}
        for c in d.get("contacts", [])
        if c.get("value")
    ]
    categories = [c.get("name_tm") for c in d.get("categories", []) if c.get("name_tm")]
    return {
        "id": d.get("id"),
        "name_tm": d.get("name_tm"),
        "name_ru": d.get("name_ru"),
        "address_tm": d.get("address_tm"),
        "categories": categories,
        "latitude": d.get("latitude"),
        "longitude": d.get("longitude"),
        "star": d.get("star"),
        "review_count": d.get("review_count"),
        "is_open": d.get("is_open"),
        "round_the_clock": d.get("round_the_clock"),
        "hours": hours,
        "contacts": contacts,
        "seo_keywords": d.get("seo_keywords"),
        "body_tm": clean_html(d.get("body_tm")),
        "slug": d.get("slug"),
        "image": d.get("image"),
        "source": "detail",
    }


def normalize_list_item(d):
    categories = [c.get("name_tm") for c in d.get("categories", []) if c.get("name_tm")]
    return {
        "id": d.get("id"),
        "name_tm": d.get("name_tm"),
        "name_ru": d.get("name_ru"),
        "address_tm": d.get("address_tm"),
        "categories": categories,
        "latitude": d.get("latitude"),
        "longitude": d.get("longitude"),
        "star": d.get("star"),
        "review_count": None,
        "is_open": d.get("is_open"),
        "round_the_clock": d.get("round_the_clock"),
        "hours": {},
        "contacts": [],
        "seo_keywords": None,
        "body_tm": "",
        "slug": d.get("slug"),
        "image": d.get("image"),
        "source": "list",
    }


def process(raw, records, stats):
    try:
        index = raw["pageProps"]["index"]
        data = index.get("data")
    except (KeyError, TypeError):
        stats["skipped_unknown"] += 1
        return

    if isinstance(data, dict) and "id" in data:
        rec = normalize_detail(data)
        rid = rec["id"]
        if rid in records and records[rid]["source"] == "detail":
            stats["duplicate_detail"] += 1
        else:
            if rid in records and records[rid]["source"] == "list":
                stats["upgraded_list_to_detail"] += 1
            records[rid] = rec
            stats["detail_count"] += 1

    elif isinstance(data, list):
        for item in data:
            rid = item.get("id")
            if rid is None:
                continue
            if rid in records:
                stats["duplicate_list"] += 1
                continue
            records[rid] = normalize_list_item(item)
            stats["list_count"] += 1
    else:
        stats["skipped_unknown"] += 1


def main():
    records = {}
    stats = {
        "detail_count": 0,
        "list_count": 0,
        "duplicate_detail": 0,
        "duplicate_list": 0,
        "upgraded_list_to_detail": 0,
        "skipped_unknown": 0,
    }

    if INPUT_DIR:
        source_iter = iter_json_files_from_dir(INPUT_DIR)
    else:
        source_iter = iter_json_files_from_zip(INPUT_ZIP)

    file_count = 0
    for name, raw in source_iter:
        file_count += 1
        process(raw, records, stats)

    null_latlong = sum(
        1 for r in records.values() if r["latitude"] is None or r["longitude"] is None
    )

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as out:
        for rec in records.values():
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"files read:              {file_count}")
    print(f"unique locations:        {len(records)}")
    print(f"  - from detail files:   {stats['detail_count']}")
    print(f"  - from list-only:      {stats['list_count']}")
    print(f"duplicate detail hits:   {stats['duplicate_detail']}")
    print(f"duplicate list hits:     {stats['duplicate_list']}")
    print(f"list upgraded to detail: {stats['upgraded_list_to_detail']}")
    print(f"skipped/unknown format:  {stats['skipped_unknown']}")
    print(f"null lat/long:           {null_latlong}")
    print(f"output written to:       {OUTPUT_JSONL}")


if __name__ == "__main__":
    main()