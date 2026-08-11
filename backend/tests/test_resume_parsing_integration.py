import pytest

from tests.pdf_builder import build_test_pdf

RESUME_LINES = [
    "John Smith",
    "john.smith@example.com",
    "EDUCATION",
    "B.Tech Computer Science, Test University, 2026",
    "EXPERIENCE",
    "Backend Intern, Test Corp, worked with Python and Docker for 2 years",
    "SKILLS",
    "Python, React, MongoDB, Git",
]


@pytest.fixture(autouse=True)
def isolate_local_storage(tmp_path, monkeypatch):
    from app.services import storage_service

    monkeypatch.setattr(storage_service.settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    yield tmp_path


async def _register_login_student(client, email="parsing.student@college.edu"):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": email,
            "password": "StrongPass123",
            "name": "Parsing Student",
            "department": "CS",
            "batch_year": 2026,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    return login.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_upload_triggers_parsing_and_detail_reflects_it(client):
    """
    This is the one test in the suite that depends on PyMuPDF/pdfplumber
    correctly reading a hand-crafted PDF (see tests/pdf_builder.py) rather
    than pure string logic — if PyMuPDF's behavior differs from what's
    assumed here, this is the test to look at first.
    """
    token = await _register_login_student(client)
    pdf_bytes = build_test_pdf(RESUME_LINES)

    upload = await client.post(
        "/api/v1/resumes",
        headers=_auth_headers(token),
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 201
    resume_id = upload.json()["id"]

    detail = await client.get(f"/api/v1/resumes/{resume_id}", headers=_auth_headers(token))
    assert detail.status_code == 200
    body = detail.json()

    assert body["parsed"] is not None
    assert body["parsed"]["email"] == "john.smith@example.com"
    assert "Python" in body["skill_set"]
    assert "MongoDB" in body["skill_set"]


@pytest.mark.asyncio
async def test_reparse_endpoint_works(client):
    token = await _register_login_student(client, email="reparse@college.edu")
    pdf_bytes = build_test_pdf(RESUME_LINES)

    upload = await client.post(
        "/api/v1/resumes",
        headers=_auth_headers(token),
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    resume_id = upload.json()["id"]

    response = await client.post(f"/api/v1/resumes/{resume_id}/reparse", headers=_auth_headers(token))
    assert response.status_code == 200
    assert response.json()["parsed"]["email"] == "john.smith@example.com"


@pytest.mark.asyncio
async def test_reparse_requires_ownership(client):
    token_a = await _register_login_student(client, email="owner@college.edu")
    pdf_bytes = build_test_pdf(RESUME_LINES)
    upload = await client.post(
        "/api/v1/resumes",
        headers=_auth_headers(token_a),
        files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
    )
    resume_id = upload.json()["id"]

    token_b = await _register_login_student(client, email="not.owner@college.edu")
    response = await client.post(f"/api/v1/resumes/{resume_id}/reparse", headers=_auth_headers(token_b))
    assert response.status_code == 403
