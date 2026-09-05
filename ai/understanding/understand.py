from rules import rule_based_extract
from llm_fallback import llm_fallback

REFUSE_MESSAGE = "Näme gözleýäniňizi has anyk aýdyp bilersiňizmi?"


def understand_query(query):
    result = rule_based_extract(query)

    if result["category"] is not None:
        result["source"] = "rule_based"
        result["refuse"] = False
        return result

    llm_result = llm_fallback(query)

    if llm_result["category"] is None:
        return {
            "category": None,
            "sort_by": None,
            "open_now_only": False,
            "source": "llm_fallback",
            "refuse": True,
            "message": REFUSE_MESSAGE,
        }

    llm_result["source"] = "llm_fallback"
    llm_result["refuse"] = False
    return llm_result