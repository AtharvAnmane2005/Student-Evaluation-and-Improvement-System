from datetime import datetime, timedelta

import pytest

from app.ml.matching.skill_ontology import canonical_skill, to_skill_set
from app.services.matching_service import build_jd_text, build_resume_text, exp_fit

FUTURE_DEADLINE = (datetime.utcnow() + timedelta(days=30)).isoformat()
MINIMAL_PDF_BYTES = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _register_login_student(client, email):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": email,
            "password": "StrongPass123",
            "name": "Matching Student",
            "department": "CS",
            "batch_year": 2026,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    return login.json()["access_token"]


async def _register_login_tpo(client, email):
    await client.post(
        "/api/v1/auth/register/tpo",
        json={"email": email, "password": "StrongPass123", "name": "Matching TPO", "department_scope": []},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    return login.json()["access_token"]


async def _upload_resume_with_skills(client, token, skills, experience_years=2.0):
    """Uploads a (fake, unparseable) PDF, then directly sets skill_set/
    experience_years on the stored document — same idea as bypassing real
    parsing that the rest of the test suite already relies on
    (MINIMAL_PDF_BYTES has no extractable text), just extended to give
    matching tests realistic skill data to actually match against."""
    from app.core import database as db_module
    from app.repositories.resume_repository import ResumeRepository

    upload = await client.post(
        "/api/v1/resumes",
        headers=_auth_headers(token),
        files={"file": ("resume.pdf", MINIMAL_PDF_BYTES, "application/pdf")},
    )
    resume_id = upload.json()["id"]
    await ResumeRepository(db_module.mongodb.db).update_by_id(
        resume_id, {"skill_set": skills, "experience_years": experience_years}
    )
    return resume_id


def _drive_payload(**overrides):
    payload = {
        "company_name": "Matching Corp",
        "job_title": "Backend Engineer",
        "description": "Build and maintain backend services for our platform.",
        "jd_text": "We need a backend engineer with Python and API experience.",
        "required_skills": ["Python", "FastAPI", "MongoDB"],
        "experience_required_years": 2.0,
        "eligibility": {},
        "deadline": FUTURE_DEADLINE,
        "selection_process": [],
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Pure-function tests — no model inference, fast, exact ports of notebook logic
# ---------------------------------------------------------------------------
def test_skill_canonicalization_matches_notebook_aliases():
    assert canonical_skill("React.js") == "react"
    assert canonical_skill("JS") == "javascript"
    assert canonical_skill("XGBoost") == "gradient boosting"
    assert canonical_skill("Docker") == "docker"  # unknown term falls back to identity


def test_to_skill_set_dedups_and_filters_empty():
    result = to_skill_set(["React.js", "ReactJS", "", "  ", "Docker"])
    assert result == {"react", "docker"}


def test_exp_fit_matches_notebook_formula():
    assert exp_fit(3.0, 0.0) == 1.0  # no requirement -> full credit
    assert exp_fit(1.0, 2.0) == 0.5  # half of required
    assert exp_fit(5.0, 2.0) == 1.0  # clamped at 1.0, not >1
    assert exp_fit(0.0, 2.0) == 0.0


def test_build_resume_text_omits_domain_and_sorts_skills():
    text = build_resume_text(["python", "docker"], 3.0)
    assert text == "Technical skills: docker, python. Experience years: 3.0"


def test_build_jd_text_omits_domain_and_sorts_skills():
    text = build_jd_text("Backend Engineer", "Acme", "Build things.", ["python", "aws"], 2.0)
    assert "Job title: Backend Engineer" in text
    assert "Required skills: aws, python" in text
    assert "Experience required: 2.0" in text


# ---------------------------------------------------------------------------
# Integration tests — real model inference against the artifacts in this
# checkout (see app/ml/matching/artifacts/README.md). Slower than the rest
# of the suite (model load + forward passes), by design.
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_drive_match_score_returns_full_breakdown(client):
    tpo_token = await _register_login_tpo(client, "match.tpo@college.edu")
    drive_response = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload()
    )
    drive_id = drive_response.json()["id"]

    student_token = await _register_login_student(client, "match.student@college.edu")
    await _upload_resume_with_skills(client, student_token, ["Python", "FastAPI", "React"], experience_years=3.0)

    response = await client.get(f"/api/v1/matching/drives/{drive_id}/score", headers=_auth_headers(student_token))
    assert response.status_code == 200
    data = response.json()

    assert set(data.keys()) >= {
        "drive_id",
        "final_score",
        "semantic_score",
        "skills_score",
        "experience_score",
        "matched_skills",
        "missing_skills",
    }
    assert 0.0 <= data["final_score"] <= 1.0
    assert 0.0 <= data["semantic_score"] <= 1.0
    # Resume has Python+FastAPI (2 of 3 required skills; MongoDB missing).
    assert set(data["matched_skills"]) == {"python", "fastapi"}
    assert data["missing_skills"] == ["mongodb"]
    assert data["skills_score"] == pytest.approx(2 / 3)
    assert data["experience_score"] == 1.0  # 3 years vs 2 required, clamped


@pytest.mark.asyncio
async def test_score_requires_a_resume(client):
    tpo_token = await _register_login_tpo(client, "noresume.tpo@college.edu")
    drive_response = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload()
    )
    drive_id = drive_response.json()["id"]

    student_token = await _register_login_student(client, "noresume.student@college.edu")
    response = await client.get(f"/api/v1/matching/drives/{drive_id}/score", headers=_auth_headers(student_token))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_recommended_drives_are_sorted_descending(client):
    tpo_token = await _register_login_tpo(client, "rec.tpo@college.edu")
    await client.post(
        "/api/v1/drives",
        headers=_auth_headers(tpo_token),
        json=_drive_payload(job_title="Strong Match", required_skills=["Python", "FastAPI"]),
    )
    await client.post(
        "/api/v1/drives",
        headers=_auth_headers(tpo_token),
        json=_drive_payload(job_title="Weak Match", required_skills=["Java", "Spring", "Kubernetes"]),
    )

    student_token = await _register_login_student(client, "rec.student@college.edu")
    await _upload_resume_with_skills(client, student_token, ["Python", "FastAPI"], experience_years=2.0)

    response = await client.get("/api/v1/matching/recommended-drives", headers=_auth_headers(student_token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    scores = [d["final_score"] for d in data]
    assert scores == sorted(scores, reverse=True)
    assert data[0]["job_title"] == "Strong Match"


@pytest.mark.asyncio
async def test_ranked_applicants_only_visible_to_owning_tpo(client):
    owner_token = await _register_login_tpo(client, "ranked.owner@college.edu")
    other_token = await _register_login_tpo(client, "ranked.other@college.edu")
    drive_response = await client.post(
        "/api/v1/drives", headers=_auth_headers(owner_token), json=_drive_payload()
    )
    drive_id = drive_response.json()["id"]

    student_token = await _register_login_student(client, "ranked.student@college.edu")
    await _upload_resume_with_skills(client, student_token, ["Python", "FastAPI", "MongoDB"], experience_years=2.0)
    await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))

    owner_response = await client.get(
        f"/api/v1/matching/drives/{drive_id}/ranked-applicants", headers=_auth_headers(owner_token)
    )
    assert owner_response.status_code == 200
    applicants = owner_response.json()
    assert len(applicants) == 1
    assert applicants[0]["student_name"] == "Matching Student"
    assert set(applicants[0]["matched_skills"]) == {"python", "fastapi", "mongodb"}

    other_response = await client.get(
        f"/api/v1/matching/drives/{drive_id}/ranked-applicants", headers=_auth_headers(other_token)
    )
    assert other_response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_access_ranked_applicants(client):
    tpo_token = await _register_login_tpo(client, "noaccess.tpo@college.edu")
    drive_response = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload()
    )
    drive_id = drive_response.json()["id"]

    student_token = await _register_login_student(client, "noaccess.student@college.edu")
    response = await client.get(
        f"/api/v1/matching/drives/{drive_id}/ranked-applicants", headers=_auth_headers(student_token)
    )
    assert response.status_code == 403
