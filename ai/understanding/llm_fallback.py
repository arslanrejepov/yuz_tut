import json
import re


MODEL_PATH = "models/gemma-4-e2b-q4_0.gguf"

_llm = None

SYSTEM_PROMPT = """Sen kategoriýa kesgitleýji assistant.
Saňa berlen sözlemi şu kategoriýalaryň biri bilen deňeşdir: {categories}

Diňe şu JSON formatda jogap ber, başga hiç zat ýazma:
{{"category": "<kategoriýa ady ýa-da null>"}}

Eger sözlem hiç bir kategoriýa gabat gelmeýän bolsa, "category" gymmatyny null goý.
Diňe berlen sanawdaky kategoriýa adyny ulan, öz sözüň bilen kategoriýa oýlap tapma."""


def _get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4, verbose=False)
    return _llm


def _extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def llm_extract_category(query, valid_categories):
    llm = _get_llm()
    system = SYSTEM_PROMPT.format(categories=", ".join(valid_categories))

    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ],
        max_tokens=60,
        temperature=0.0,
    )

    raw = output["choices"][0]["message"]["content"]
    parsed = _extract_json(raw)
    if not parsed:
        return {"category": None, "confidence": "low", "raw": raw}

    category = parsed.get("category")
    if category not in valid_categories:
        category = None

    return {
        "category": category,
        "confidence": "high" if category else "low",
        "raw": raw,
    }