"""
Skill-term normalization, replicating PLACER_RoBERTa_Training_NEW.ipynb's
CELL 4 exactly.

The notebook builds its full alias map from two sources: (1) a large list
of ~800 recognized skill terms from `ML_Keywords_and_Projects.txt`, each
mapped to itself, and (2) an explicit `manual_aliases` dict of ~18 real
synonym mappings (e.g. "reactjs" -> "react"). Source (1) never changes
behavior beyond the default identity fallback the code already has
(`ALIAS_INV.get(term, term)`), since mapping a term to itself is exactly
what happens anyway when a term isn't in the map at all. Source (2) is the
only part that does real work — and it's hardcoded directly in the
notebook, not loaded from an external file, so we have it verbatim here.

`ML_Keywords_and_Projects.txt` (and its output `keyword_ontology.json`)
weren't available when this was wired up — see PROJECT_PROGRESS.md's
Phase 7/9 section for why that's fine: this file is behaviorally
equivalent to the full notebook ontology for every term that actually
matters, i.e. terms with a real synonym to resolve. If a future terms
list surfaces, add it as an explicit CANON_TERMS set below (identity
entries only) for closer parity with the original notebook's coverage —
it won't change matching behavior, only make it slightly more literal.
"""
import re

MANUAL_ALIASES: dict[str, str] = {
    "react.js": "react",
    "reactjs": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "node js": "node.js",
    "js": "javascript",
    "ecmascript": "javascript",
    "python3": "python",
    "python 3": "python",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "scikit learn": "scikit-learn",
    "sci kit learn": "scikit-learn",
    "hf": "hugging face",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "svm": "support vector machines",
    "knn": "k-nearest neighbors",
    "xgboost": "gradient boosting",
    "lightgbm": "gradient boosting",
    "catboost": "gradient boosting",
}


def clean_term(x: str) -> str:
    """Exact port of the notebook's clean_term()."""
    x = str(x).lower().strip()
    x = x.replace("\u2019", "'")
    x = re.sub(r"\(.*?\)", "", x)
    x = re.sub(r"[^a-z0-9\+#\.\-\/\s]", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def _build_alias_map() -> dict[str, str]:
    alias_inv: dict[str, str] = {}
    for a, c in MANUAL_ALIASES.items():
        a2, c2 = clean_term(a), clean_term(c)
        if a2 and c2:
            alias_inv[a2] = c2
    # Every value also maps to itself, matching the notebook's final pass —
    # keeps canonical_skill() idempotent (canonical_skill(canonical_skill(x)) == canonical_skill(x)).
    for _, c in list(alias_inv.items()):
        alias_inv[c] = c
    return alias_inv


_ALIAS_MAP = _build_alias_map()


def canonical_skill(term: str) -> str:
    """Maps a raw skill string to its canonical form. Unknown terms fall
    back to their cleaned form (identity) — matching the notebook's
    `ALIAS_INV.get(clean_term(s), clean_term(s))` exactly."""
    cleaned = clean_term(term)
    return _ALIAS_MAP.get(cleaned, cleaned)


def to_skill_set(items: list[str]) -> set[str]:
    """Canonicalized, de-duplicated, empty-string-filtered skill set."""
    return {canonical_skill(item) for item in items if clean_term(item)}
