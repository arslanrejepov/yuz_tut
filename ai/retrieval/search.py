import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "ai/indexing/chroma_db"
COLLECTION_NAME = "locations"
MODEL_NAME = "intfloat/multilingual-e5-base"


class LocationSearch:
    def __init__(self, chroma_path: str = CHROMA_PATH, collection_name: str = COLLECTION_NAME):
        self.model = SentenceTransformer(MODEL_NAME)
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_collection(collection_name)

    def search(self, query: str, top_n: int = 10) -> list[dict]:
        query_embedding = self.model.encode(
            f"query: {query}",
            normalize_embeddings=True,
        ).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_n,
        )

        output = []
        ids = results["ids"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        documents = results["documents"][0]

        for i in range(len(ids)):
            output.append({
                "id": ids[i],
                "score": 1 - distances[i],
                "embedding_text": documents[i],
                "metadata": metadatas[i],
            })

        return output


TEST_QUERIES = [
    "dermanhana gerek",
    "gije işleýän restoran gerek",
    "8 marta sowgat alar ýaly dükan maslahat ber",
    "masynyn dowuldi haýal wagt awto serwis hyzmatyny tapyp ber",
    "elim kesildi gan akya name etmeli, yakyndan apteka",
    "arzan telefon dukany",
    "iýmit",
    "cocuk oyuncak dukany",
    "toy uçin sowgatlyk zat",
    "kofe icesim gelya",
    "gozel salon gerek",
    "kir ýuwujy maşyn abatlaýan yer",
    "cagalar bagy",
    "restoran",
    "bank",
    "kitap dukany",
    "welosiped satyn alyar yaly yer",
    "guycli internet operator",
    "diş lukmany",
    "mata we tikin esbaplary",
]


if __name__ == "__main__":
    searcher = LocationSearch()
    for query in TEST_QUERIES:
        print(f"\n=== {query} ===")
        results = searcher.search(query, top_n=5)
        for r in results:
            print(f"{r['score']:.3f}  {r['metadata'].get('name_tm')}  ({r['id']})")