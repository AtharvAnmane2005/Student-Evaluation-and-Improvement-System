"""
Best-effort resume section splitter. Real resumes use wildly inconsistent
headers ("Work Experience" vs "Employment History" vs "Experience"), so
this matches against a curated list of common variants per canonical
section rather than assuming one fixed vocabulary.
"""
import re

SECTION_HEADERS: dict[str, list[str]] = {
    "education": ["education", "academic background", "academics", "qualifications"],
    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
        "work history",
    ],
    "projects": ["projects", "academic projects", "personal projects", "key projects"],
    "skills": ["skills", "technical skills", "skill set", "core competencies", "skills summary"],
    "certifications": ["certifications", "certificates", "licenses", "certifications & licenses"],
    "achievements": ["achievements", "accomplishments", "awards", "honors", "honors & awards"],
    "languages": ["languages", "language proficiency"],
}


def _build_header_pattern() -> re.Pattern:
    all_variants = [v for variants in SECTION_HEADERS.values() for v in variants]
    # Longest first so multi-word headers ("work experience") are matched
    # before a shorter substring header ("experience") could shadow them.
    all_variants.sort(key=len, reverse=True)
    escaped = [re.escape(v) for v in all_variants]
    return re.compile(rf"^\s*({'|'.join(escaped)})\s*:?\s*$", re.IGNORECASE)


HEADER_PATTERN = _build_header_pattern()


def _canonical_section(header_text: str) -> str | None:
    header_lower = header_text.strip().lower()
    for canonical, variants in SECTION_HEADERS.items():
        if header_lower in variants:
            return canonical
    return None


def split_into_sections(text: str) -> dict[str, str]:
    """
    Scans line by line; a line that exactly matches a known header phrase
    (short, standalone — typical of how resumes actually format section
    headers) starts a new section. Content before the first recognized
    header is not attributed to any section (it's still in the full
    resume_text, just not section-tagged).
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in text.splitlines():
        stripped = line.strip()
        match = HEADER_PATTERN.match(stripped)
        if match:
            canonical = _canonical_section(match.group(1))
            if canonical:
                current = canonical
                sections.setdefault(current, [])
                continue
        if current:
            sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}
