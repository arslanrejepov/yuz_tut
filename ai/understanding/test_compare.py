"""
A/B comparison: raw query embedding vs rule-based-extracted-category embedding.

Assumes ai/retrieval/search.py exposes a class LocationSearch with a method
    search(query: str, top_n: int = 5) -> list[dict]
where each dict has at least: name_tm (or similar), score.

Adjust the import path / method call below to match your actual search.py API
if it differs.
"""

from understanding.rules import rule_based_extract
from retrieval.search import LocationSearch

TEST_QUERIES = [
    "pizza gerek",
    "iň arzan pizza nirede",
    "gije işleýän restoran",
    "arzan telefon dükany",
    "iň ýakyn dermanhana",
    "kofe içesim gelýär",
    "täze aýakgap almaly",
    "çaga üçin oýnawaç",
    "toý üçin salon gerek",
    "iň gowy gözellik salony",
    "maşynym döwüldi",
    "maşyn abatlamak gerek",
    "benzin gutardy",
    "gije açyk market barmy",
    "dogan-garyndaşym üçin sowgat gerek",
    "sowgatlyk dükany",
    "gül buketi sargyt etmek isleýärin",
    "iň ýakyn bank",
    "kredit almak isleýärin",
    "noutbuk abatlaýyş",
    "täze telefon satyn almak",
    "burger sargyt etmek",
    "döner nirede satylýar",
    "iň arzan suşi",
    "steýk iýesim gelýär",
    "milli tagam iýmek isleýärin",
    "türk restorany gözleýärin",
    "aziýa restorany",
    "kitap dükany",
    "sagat dükany golaýda barmy",
    "haly satyn almak isleýärin",
    "mebel dükany",
    "hojalyk tehnikalary satylýan ýer",
    "kir ýuwujy machine gerek",
    "kompýuter dükany",
    "web sahypa ýasadyp bilýän ýer",
    "foto düşürmek üçin studio",
    "aýdymçy kärendesine almak isleýärin",
    "karaoke barmy şäherde",
    "söwda merkezi nirede",
    "eltip bermek hyzmaty barmy",
    "himiki arassalaýyş nirede",
    "emläk agentligi gözleýärin",
    "kwartira almak isleýärin",
    "optika dükany",
    "äýnek almaly",
    "kino görmek isleýärin",
    "dogum güni üçin tort sargyt etmek",
    "doňdurma iýesim gelýär",
]


def top_result_name(results):
    if not results:
        return None, None
    r = results[0]
    name = r.get("metadata", {}).get("name_tm") or r.get("name_tm") or r.get("id")
    score = r.get("score")
    return name, score


def run():
    searcher = LocationSearch()

    print(f"{'QUERY':45} | {'RAW top-1 (score)':40} | {'RULE category':25} | {'RULE top-1 (score)':40}")
    print("-" * 155)

    for q in TEST_QUERIES:
        raw_results = searcher.search(q, top_n=1)
        raw_name, raw_score = top_result_name(raw_results)
        raw_str = f"{raw_name} ({raw_score:.3f})" if raw_name else "NONE"

        extracted = rule_based_extract(q)
        category = extracted["category"]

        if category:
            rule_results = searcher.search(category, top_n=1)
            rule_name, rule_score = top_result_name(rule_results)
            rule_str = f"{rule_name} ({rule_score:.3f})" if rule_name else "NONE"
        else:
            rule_str = "N/A (no category matched)"

        print(f"{q:45} | {raw_str:40} | {str(category):25} | {rule_str:40}")


if __name__ == "__main__":
    run()