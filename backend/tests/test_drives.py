from datetime import datetime, timedelta

import pytest

FUTURE_DEADLINE = (datetime.utcnow() + timedelta(days=30)).isoformat()
PAST_DEADLINE = (datetime.utcnow() - timedelta(days=1)).isoformat()
MINIMAL_PDF_BYTES = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"


async def _register_login_student(client, email, department="CS", batch_year=2026, cgpa=None):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": email,
            "password": "StrongPass123",
            "name": "Test Student",
            "department": department,
            "batch_year": batch_year,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    token = login.json()["access_token"]
    if cgpa is not None:
        # No profile-update endpoint yet (Phase 12+); write directly for test setup.
        from app.core import database as db_module

        await db_module.mongodb.db.students.update_one(
            {"user_id": login.json()["user"]["id"]}, {"$set": {"cgpa": cgpa}}
        )
    return token


async def _register_login_tpo(client, email="drive.tpo@college.edu"):
    await client.post(
        "/api/v1/auth/register/tpo",
        json={"email": email, "password": "StrongPass123", "name": "TPO User", "department_scope": []},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    return login.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _drive_payload(**overrides):
    payload = {
        "company_name": "Acme Corp",
        "company_description": "A widget company",
        "job_title": "Software Engineer",
        "description": "Build things",
        "jd_text": "We need a software engineer skilled in Python and React.",
        "required_skills": ["Python", "React"],
        "package": "12 LPA",
        "location": "Remote",
        "eligibility": {"min_cgpa": 7.0, "departments": [], "batch_years": []},
        "deadline": FUTURE_DEADLINE,
        "selection_process": ["Online Test", "Interview"],
    }
    payload.update(overrides)
    return payload


@pytest.mark.asyncio
async def test_tpo_can_create_drive(client):
    token = await _register_login_tpo(client)
    response = await client.post("/api/v1/drives", headers=_auth_headers(token), json=_drive_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["company"]["name"] == "Acme Corp"
    assert body["job_title"] == "Software Engineer"
    assert body["status"] == "open"


@pytest.mark.asyncio
async def test_student_cannot_create_drive(client):
    token = await _register_login_student(client, "nocreate@college.edu")
    response = await client.post("/api/v1/drives", headers=_auth_headers(token), json=_drive_payload())
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reusing_company_name_does_not_duplicate_company(client):
    token = await _register_login_tpo(client, email="reuse.tpo@college.edu")
    first = await client.post(
        "/api/v1/drives", headers=_auth_headers(token), json=_drive_payload(job_title="Role A")
    )
    second = await client.post(
        "/api/v1/drives", headers=_auth_headers(token), json=_drive_payload(job_title="Role B")
    )
    assert first.json()["company"]["id"] == second.json()["company"]["id"]


@pytest.mark.asyncio
async def test_list_drives_returns_created_drive(client):
    token = await _register_login_tpo(client, email="list.tpo@college.edu")
    await client.post("/api/v1/drives", headers=_auth_headers(token), json=_drive_payload())

    student_token = await _register_login_student(client, "lister@college.edu")
    response = await client.get("/api/v1/drives", headers=_auth_headers(student_token))
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_only_owner_tpo_can_update_drive(client):
    owner_token = await _register_login_tpo(client, email="owner.tpo@college.edu")
    create = await client.post("/api/v1/drives", headers=_auth_headers(owner_token), json=_drive_payload())
    drive_id = create.json()["id"]

    other_token = await _register_login_tpo(client, email="other.tpo@college.edu")
    forbidden = await client.put(
        f"/api/v1/drives/{drive_id}", headers=_auth_headers(other_token), json={"package": "20 LPA"}
    )
    assert forbidden.status_code == 403

    allowed = await client.put(
        f"/api/v1/drives/{drive_id}", headers=_auth_headers(owner_token), json={"package": "20 LPA"}
    )
    assert allowed.status_code == 200
    assert allowed.json()["package"] == "20 LPA"


@pytest.mark.asyncio
async def test_only_owner_tpo_can_delete_drive(client):
    owner_token = await _register_login_tpo(client, email="del.owner@college.edu")
    create = await client.post("/api/v1/drives", headers=_auth_headers(owner_token), json=_drive_payload())
    drive_id = create.json()["id"]

    other_token = await _register_login_tpo(client, email="del.other@college.edu")
    forbidden = await client.delete(f"/api/v1/drives/{drive_id}", headers=_auth_headers(other_token))
    assert forbidden.status_code == 403

    allowed = await client.delete(f"/api/v1/drives/{drive_id}", headers=_auth_headers(owner_token))
    assert allowed.status_code == 204


@pytest.fixture(autouse=True)
def isolate_local_storage(tmp_path, monkeypatch):
    from app.services import storage_service

    monkeypatch.setattr(storage_service.settings, "LOCAL_STORAGE_PATH", str(tmp_path))
    yield tmp_path


async def _upload_resume(client, token):
    return await client.post(
        "/api/v1/resumes",
        headers=_auth_headers(token),
        files={"file": ("resume.pdf", MINIMAL_PDF_BYTES, "application/pdf")},
    )


@pytest.mark.asyncio
async def test_apply_succeeds_when_eligible_with_resume(client):
    tpo_token = await _register_login_tpo(client, email="apply.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "eligible@college.edu")
    await _upload_resume(client, student_token)

    response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    assert response.status_code == 201
    assert response.json()["status"] == "applied"


@pytest.mark.asyncio
async def test_apply_fails_without_resume(client):
    tpo_token = await _register_login_tpo(client, email="noresume.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "noresume@college.edu")
    response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_apply_fails_when_cgpa_below_minimum(client):
    tpo_token = await _register_login_tpo(client, email="cgpa.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives",
        headers=_auth_headers(tpo_token),
        json=_drive_payload(eligibility={"min_cgpa": 9.0}),
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "lowcgpa@college.edu", cgpa=6.5)
    await _upload_resume(client, student_token)

    response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_apply_fails_when_department_not_eligible(client):
    tpo_token = await _register_login_tpo(client, email="dept.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives",
        headers=_auth_headers(tpo_token),
        json=_drive_payload(eligibility={"departments": ["Electronics"]}),
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "wrongdept@college.edu", department="CS")
    await _upload_resume(client, student_token)

    response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_apply_fails_after_deadline(client):
    tpo_token = await _register_login_tpo(client, email="deadline.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives",
        headers=_auth_headers(tpo_token),
        json=_drive_payload(eligibility={}, deadline=PAST_DEADLINE),
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "late@college.edu")
    await _upload_resume(client, student_token)

    response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_duplicate_application_rejected(client):
    tpo_token = await _register_login_tpo(client, email="dupapp.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "dupapplicant@college.edu")
    await _upload_resume(client, student_token)

    first = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    second = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_student_can_see_own_applications(client):
    tpo_token = await _register_login_tpo(client, email="myapps.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "myapplicant@college.edu")
    await _upload_resume(client, student_token)
    await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))

    response = await client.get("/api/v1/drives/applications/me", headers=_auth_headers(student_token))
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_only_owner_tpo_can_view_drive_applications(client):
    owner_token = await _register_login_tpo(client, email="viewapps.owner@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(owner_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "viewedapplicant@college.edu")
    await _upload_resume(client, student_token)
    await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))

    other_tpo_token = await _register_login_tpo(client, email="viewapps.other@college.edu")
    forbidden = await client.get(
        f"/api/v1/drives/{drive_id}/applications", headers=_auth_headers(other_tpo_token)
    )
    assert forbidden.status_code == 403

    allowed = await client.get(
        f"/api/v1/drives/{drive_id}/applications", headers=_auth_headers(owner_token)
    )
    assert allowed.status_code == 200
    assert len(allowed.json()) == 1


# ---------------------------------------------------------------------------
# Phase 13 — TPO dashboard additions: /drives/mine and applicant status updates
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_my_drives_returns_only_own_drives(client):
    owner_token = await _register_login_tpo(client, email="mine.owner@college.edu")
    other_token = await _register_login_tpo(client, email="mine.other@college.edu")

    await client.post("/api/v1/drives", headers=_auth_headers(owner_token), json=_drive_payload())
    await client.post("/api/v1/drives", headers=_auth_headers(other_token), json=_drive_payload())

    response = await client.get("/api/v1/drives/mine", headers=_auth_headers(owner_token))
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_student_cannot_list_drives_mine(client):
    student_token = await _register_login_student(client, "notpo@college.edu")
    response = await client.get("/api/v1/drives/mine", headers=_auth_headers(student_token))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_drive_applications_include_student_and_resume_details(client):
    tpo_token = await _register_login_tpo(client, email="detail.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "detailapplicant@college.edu", department="CS")
    await _upload_resume(client, student_token)
    await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))

    response = await client.get(f"/api/v1/drives/{drive_id}/applications", headers=_auth_headers(tpo_token))
    assert response.status_code == 200
    applicant = response.json()[0]
    assert applicant["student_name"] == "Test Student"
    assert applicant["student_department"] == "CS"
    assert applicant["resume_filename"] == "resume.pdf"


@pytest.mark.asyncio
async def test_owner_tpo_can_update_application_status(client):
    tpo_token = await _register_login_tpo(client, email="status.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "statusapplicant@college.edu")
    await _upload_resume(client, student_token)
    apply_response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    application_id = apply_response.json()["id"]

    response = await client.patch(
        f"/api/v1/drives/{drive_id}/applications/{application_id}",
        headers=_auth_headers(tpo_token),
        json={"status": "shortlisted"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "shortlisted"


@pytest.mark.asyncio
async def test_non_owner_tpo_cannot_update_application_status(client):
    owner_token = await _register_login_tpo(client, email="statusowner.tpo@college.edu")
    other_token = await _register_login_tpo(client, email="statusother.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(owner_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "statusother@college.edu")
    await _upload_resume(client, student_token)
    apply_response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    application_id = apply_response.json()["id"]

    response = await client.patch(
        f"/api/v1/drives/{drive_id}/applications/{application_id}",
        headers=_auth_headers(other_token),
        json={"status": "rejected"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_update_application_status(client):
    tpo_token = await _register_login_tpo(client, email="statusstudentcheck.tpo@college.edu")
    drive = await client.post(
        "/api/v1/drives", headers=_auth_headers(tpo_token), json=_drive_payload(eligibility={})
    )
    drive_id = drive.json()["id"]

    student_token = await _register_login_student(client, "statuscheck@college.edu")
    await _upload_resume(client, student_token)
    apply_response = await client.post(f"/api/v1/drives/{drive_id}/apply", headers=_auth_headers(student_token))
    application_id = apply_response.json()["id"]

    response = await client.patch(
        f"/api/v1/drives/{drive_id}/applications/{application_id}",
        headers=_auth_headers(student_token),
        json={"status": "selected"},
    )
    assert response.status_code == 403
