"""
Critical-urgency safety override — Medical Triage NLU
========================================================
Independent, rule-based check that runs ALONGSIDE the XLM-R model at
inference time, not instead of it. If either the model OR this check
says "critical", the pipeline treats it as critical.

This exists because a single neural model's confidence should never be
the only thing standing between an emergency message and a safe outcome.
Patterns below are built from real phrases found in the critical-labeled
rows of the training data — extend this list as you see more.

USAGE:
    from critical_override import check_critical_override

    is_critical = check_critical_override(user_text) or model_prediction == "critical"
"""

import re

# Patterns grouped by category for maintainability. Case-insensitive match.
# Extend these from real critical-labeled examples in your dataset — this
# is a starting set, not exhaustive.
CRITICAL_PATTERNS = [
    # breathing difficulty (Turkmen + Russian)
    r"dem al\w* (kyn|bilemok|kynla)",
    r"dem\w* ýetenok",
    r"одышка",
    r"суффокация|suffocation",
    r"gys[yı]l\w* dem",

    # chest pain radiating / cardiac signs
    r"döş\w* agr\w*.*(elim|çep)",
    r"ýüreg\w* gaty ur",
    r"press\w* agr\w*",

    # loss of consciousness
    r"huş\w* ýitir",
    r"эсс?e?ни ýitir",
    r"ýatdy.*(şowly|turmady|turmaýar)",
    r"tönäp ýatyr",

    # severe bleeding
    r"gaty köp gan",
    r"gan\w* saklan\w*",
    r"miska döwül",  # example: severe cut context

    # explicit emergency-seeking language
    r"skory|скорую|скорая",
    r"kömek gerek.*(gaty|çyndan)",
    r"gorkýan|gorkyly",

    # high fever in a child (context-sensitive, kept narrow to reduce false positives)
    r"balam.*yssy\w*.*3[9]",
    r"çaga.*yssy\w*.*4[0-9]",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in CRITICAL_PATTERNS]


def check_critical_override(text: str) -> bool:
    """
    Returns True if the raw text matches a known red-flag pattern.
    This should be OR'd with the model's own prediction — never used
    to override a model prediction of "critical" down to something lower.
    """
    if not text:
        return False
    return any(pattern.search(text) for pattern in _COMPILED)


def get_matched_patterns(text: str) -> list[str]:
    """
    For logging/auditability — returns which pattern(s) fired, so triage
    decisions can be reviewed and the safety layer stays explainable.
    """
    if not text:
        return []
    return [p.pattern for p in _COMPILED if p.search(text)]


if __name__ == "__main__":
    # quick smoke test against a few examples from your critical spot-check
    test_cases = [
        "döşüm gysylýar dem alyp bilemok kömek gerek gaty erbet",
        "balam intäk kiçi yssysy 39 boldy skory çagyrsaňyzla",
        "başym biraz agyrýar, düýn agşamdan bäri",  # should NOT trigger
    ]
    for t in test_cases:
        result = check_critical_override(t)
        print(f"[{result}] {t}")
        if result:
            print(f"    matched: {get_matched_patterns(t)}")