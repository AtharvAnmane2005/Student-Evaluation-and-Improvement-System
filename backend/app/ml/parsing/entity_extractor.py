"""
Extracts the candidate's name from the top of the resume.

spaCy's small English model does PERSON-entity recognition reasonably
well for this narrow use case (a name near the very top of a document).
The model is a separate download (`python -m spacy download en_core_web_sm`)
from the `spacy` pip package itself — if it's missing, we fall back to a
simple heuristic rather than crashing, since a resume upload succeeding
should never depend on an NLP model being present.
"""
import logging

logger = logging.getLogger(__name__)

_nlp = None
_load_attempted = False


def _get_nlp():
    global _nlp, _load_attempted
    if _load_attempted:
        return _nlp
    _load_attempted = True
    try:
        import spacy

        _nlp = spacy.load("en_core_web_sm")
    except Exception as exc:  # model not downloaded, or spaCy itself missing
        logger.warning(
            "spaCy model 'en_core_web_sm' unavailable (%s) — falling back to a "
            "heuristic for name extraction. Run: python -m spacy download en_core_web_sm",
            exc,
        )
        _nlp = None
    return _nlp


def _heuristic_name(text: str) -> str | None:
    """First non-empty line that looks like a name: no digits, no '@',
    1-5 words. Resumes almost universally lead with the candidate's name
    as the very first line."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "@" in stripped or any(ch.isdigit() for ch in stripped):
            return None  # first content line looks like contact info, not a name
        words = stripped.split()
        if 1 <= len(words) <= 5:
            return stripped
        return None
    return None


def extract_name(text: str) -> str | None:
    head = text[:300]  # a resume's name is always near the very top
    nlp = _get_nlp()
    if nlp:
        doc = nlp(head)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()

    return _heuristic_name(text)
