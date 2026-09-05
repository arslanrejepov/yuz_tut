import json
import re
import ollama

from rules import CATEGORY_SYNONYMS

MODEL_NAME = "hf.co/google/gemma-4-E2B-it-qat-q4_0-gguf"

VALID_CATEGORIES = list(CATEGORY_SYNONYMS.keys())

SYSTEM_PROMPT = """Sen kategoriýa we sort maksadyny kesgitleýän assistant.
Diňe şu kategoriýalaryň arasyndan saýla: {categories}

Diňe şu JSON formatda jogap ber, başga hiç zat ýazma, düşündiriş goşma:
{{"category": "<kategoriýa ady ýa-da null>", "sort_by": "<sort_by_rating|sort_by_price_asc|sort_by_distance|null>", "open_now_only": <true ýa-da false>}}

Eger sözlem hiç bir kategoriýa gabat gelmeýän bolsa, "category" gymmatyny null goý.
Diňe berlen sanawdaky kategoriýa adyny ulan, öz sözüň bilen kategoriýa oýlap tapma."""


def _extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def llm_fallback(query):
    system = SYSTEM_PROMPT.format(categories=", ".join(VALID_CATEGORIES))

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        options={"temperature": 0.0},
    )

    raw = response["message"]["content"]
    parsed = _extract_json(raw)

    if not parsed:
        return {"category": None, "sort_by": None, "open_now_only": False}

    category = parsed.get("category")
    if category not in VALID_CATEGORIES:
        category = None

    sort_by = parsed.get("sort_by")
    if sort_by not in ("sort_by_rating", "sort_by_price_asc", "sort_by_distance"):
        sort_by = None

    open_now_only = bool(parsed.get("open_now_only", False))

    return {
        "category": category,
        "sort_by": sort_by,
        "open_now_only": open_now_only,
    }