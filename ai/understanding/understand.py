from understanding.rules import rule_based_extract, CATEGORY_SYNONYMS
from understanding.llm_fallback import llm_extract_category

VALID_CATEGORIES = list(CATEGORY_SYNONYMS.keys())


def understand_query(query):
    result = rule_based_extract(query)

    if result["category"] is not None:
        result["source"] = "rule_based"
        return result

    llm_result = llm_extract_category(query, VALID_CATEGORIES)
    result["category"] = llm_result["category"]
    result["confidence"] = llm_result["confidence"]
    result["source"] = "llm_fallback"
    return result


if __name__ == "__main__":
    tests = [
        "gije işleýän arzan restoran gerek",
        "elim kesildi gan akýar",
        "iň ýakyn dermanhana",
        "maşynym döwüldi",
    ]
    for t in tests:
        print(t, "->", understand_query(t))