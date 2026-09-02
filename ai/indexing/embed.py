import json
import chromadb
from sentence_transformers import SentenceTransformer

JSONL_PATH = "../../data/locations_embedding_ready.jsonl"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "locations"
MODEL_NAME = "intfloat/multilingual-e5-base"
BATCH_SIZE = 64


def load_records(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def flatten_metadata(record):
    metadata = dict(record.get("metadata", {}))
    clean = {}
    for k, v in metadata.items():
        if v is None:
            continue
        if k == "categories" and isinstance(v, list):
            clean[k] = ", ".join(str(x) for x in v)
        elif isinstance(v, (str, int, float, bool)):
            clean[k] = v
        else:
            clean[k] = json.dumps(v, ensure_ascii=False)
    return clean


def main():
    print("loading records...")
    records = load_records(JSONL_PATH)
    print(f"{len(records)} records loaded")

    print("loading model...")
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        ids = [str(r["id"]) for r in batch]
        texts = [f"passage: {r['embedding_text']}" for r in batch]
        metadatas = [flatten_metadata(r) for r in batch]

        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[r["embedding_text"] for r in batch],
            metadatas=metadatas,
        )

        print(f"{min(i + BATCH_SIZE, len(records))}/{len(records)}")

    print("done. count:", collection.count())


if __name__ == "__main__":
    main()