"""
Orchestrates the full extraction pipeline: PDF -> text -> sections ->
structured fields. Deliberately never raises for an ordinary readable-but-
messy resume — a parsing hiccup should degrade to empty/null fields, not
block an upload that already succeeded in Phase 5.
"""
import re

from app.ml.parsing.contact_extractor import extract_email, extract_phone
from app.ml.parsing.entity_extractor import extract_name
from app.ml.parsing.section_parser import split_into_sections
from app.ml.parsing.skill_normalizer import extract_skills
from app.ml.parsing.text_extraction import extract_text
from app.models.resume import ParsedResumeData


def _split_entries(section_text: str) -> list[str]:
    """One entry per non-empty line/bullet within a section."""
    entries = []
    for line in section_text.splitlines():
        stripped = line.strip(" \t-•*").strip()
        if stripped:
            entries.append(stripped)
    return entries


EXPERIENCE_YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\+?\s*years?", re.IGNORECASE)


def _estimate_experience_years(experience_entries: list[str]) -> float | None:
    """
    Rough heuristic: looks for an explicit "N years" phrase in the
    Experience section. Real date-range parsing (e.g. "Jan 2022 - Present")
    is a reasonable future improvement once there's labeled data to
    validate it against — flagged as a follow-up rather than shipped as an
    unvalidated guess dressed up as precision.
    """
    combined = " ".join(experience_entries)
    match = EXPERIENCE_YEARS_RE.search(combined)
    return float(match.group(1)) if match else None


def parse_resume(file_bytes: bytes) -> tuple[ParsedResumeData, str, list[str], float | None]:
    """Returns (parsed_data, raw_text, skill_set, experience_years)."""
    text = extract_text(file_bytes)
    sections = split_into_sections(text)

    # Scans the WHOLE resume, not just a "Skills" section — see
    # skill_normalizer.extract_skills docstring.
    skills = extract_skills(text)

    education_entries = _split_entries(sections.get("education", ""))
    experience_entries = _split_entries(sections.get("experience", ""))
    project_entries = _split_entries(sections.get("projects", ""))
    certification_entries = _split_entries(sections.get("certifications", ""))
    achievement_entries = _split_entries(sections.get("achievements", ""))
    language_entries = _split_entries(sections.get("languages", ""))

    parsed = ParsedResumeData(
        name=extract_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        education=[{"raw": e} for e in education_entries],
        experience=[{"raw": e} for e in experience_entries],
        projects=[{"raw": e} for e in project_entries],
        skills=skills,
        certifications=certification_entries,
        achievements=achievement_entries,
        languages=language_entries,
    )

    experience_years = _estimate_experience_years(experience_entries)
    return parsed, text, skills, experience_years
