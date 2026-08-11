from app.ml.parsing.contact_extractor import extract_email, extract_github, extract_linkedin, extract_phone
from app.ml.parsing.entity_extractor import _heuristic_name
from app.ml.parsing.section_parser import split_into_sections
from app.ml.parsing.skill_normalizer import extract_skills, normalize_skill

SAMPLE_RESUME_TEXT = """Jane Doe
jane.doe@gmail.com | +1 415-555-0132
linkedin.com/in/janedoe | github.com/janedoe

EDUCATION
B.Tech Computer Science, XYZ University, 2026
CGPA: 8.7/10

EXPERIENCE
Software Engineering Intern, Acme Corp
Worked on backend services using Python and FastAPI for 1.5 years.

PROJECTS
Placement Portal - Built with React, Node.js, and MongoDB
Recommendation Engine - Used scikit-learn and pandas

SKILLS
Python, JavaScript, React, MongoDB, Docker, Git

CERTIFICATIONS
AWS Certified Cloud Practitioner

ACHIEVEMENTS
Winner, Inter-College Hackathon 2025

LANGUAGES
English, Hindi
"""


# ---------------------------------------------------------------------
# contact_extractor
# ---------------------------------------------------------------------
def test_extract_email():
    assert extract_email(SAMPLE_RESUME_TEXT) == "jane.doe@gmail.com"


def test_extract_email_returns_none_when_absent():
    assert extract_email("No contact info here.") is None


def test_extract_phone():
    phone = extract_phone(SAMPLE_RESUME_TEXT)
    assert phone is not None
    assert "555" in phone


def test_extract_linkedin():
    assert extract_linkedin(SAMPLE_RESUME_TEXT) == "linkedin.com/in/janedoe"


def test_extract_github():
    assert extract_github(SAMPLE_RESUME_TEXT) == "github.com/janedoe"


# ---------------------------------------------------------------------
# section_parser
# ---------------------------------------------------------------------
def test_split_into_sections_finds_all_sections():
    sections = split_into_sections(SAMPLE_RESUME_TEXT)
    assert set(sections.keys()) == {
        "education", "experience", "projects", "skills",
        "certifications", "achievements", "languages",
    }


def test_split_into_sections_content_is_correct():
    sections = split_into_sections(SAMPLE_RESUME_TEXT)
    assert "XYZ University" in sections["education"]
    assert "Acme Corp" in sections["experience"]
    assert "Placement Portal" in sections["projects"]
    assert "AWS Certified" in sections["certifications"]


def test_split_into_sections_handles_header_variants():
    text = "WORK EXPERIENCE\nDid some work.\n\nTECHNICAL SKILLS\nPython"
    sections = split_into_sections(text)
    assert "Did some work" in sections["experience"]
    assert "Python" in sections["skills"]


def test_split_into_sections_empty_text_returns_empty_dict():
    assert split_into_sections("") == {}


# ---------------------------------------------------------------------
# skill_normalizer
# ---------------------------------------------------------------------
def test_extract_skills_finds_known_skills():
    skills = extract_skills(SAMPLE_RESUME_TEXT)
    assert "Python" in skills
    assert "React" in skills
    assert "MongoDB" in skills
    assert "Docker" in skills


def test_extract_skills_resolves_aliases():
    skills = extract_skills("I used JS and ReactJS and k8s extensively.")
    assert "JavaScript" in skills
    assert "React" in skills
    assert "Kubernetes" in skills


def test_extract_skills_no_duplicates_across_case_variants():
    skills = extract_skills("python Python PYTHON")
    assert skills.count("Python") == 1


def test_normalize_skill_passes_through_unknown_terms():
    assert normalize_skill("SomeRandomTool") == "SomeRandomTool"


def test_extract_skills_does_not_match_substrings_of_other_words():
    # "C" should not spuriously match inside "Cucumber" or similar.
    skills = extract_skills("Experience with Cucumber testing framework.")
    assert "C" not in skills


# ---------------------------------------------------------------------
# entity_extractor (heuristic fallback path — spaCy model not assumed
# available in every environment, so this exercises the fallback directly)
# ---------------------------------------------------------------------
def test_heuristic_name_picks_first_clean_line():
    assert _heuristic_name(SAMPLE_RESUME_TEXT) == "Jane Doe"


def test_heuristic_name_returns_none_if_first_line_is_contact_info():
    text = "jane.doe@gmail.com\nSome other content"
    assert _heuristic_name(text) is None


def test_heuristic_name_returns_none_for_long_first_line():
    text = "This is a long sentence that is clearly not a name at all here"
    assert _heuristic_name(text) is None
