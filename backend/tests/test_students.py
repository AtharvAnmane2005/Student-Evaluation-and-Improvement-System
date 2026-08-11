import pytest


async def _register_login_student(client, email="profile.student@college.edu"):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": email,
            "password": "StrongPass123",
            "name": "Profile Student",
            "department": "CS",
            "batch_year": 2026,
        },
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    return login.json()["access_token"]


async def _register_login_tpo(client, email="profile.tpo@college.edu"):
    await client.post(
        "/api/v1/auth/register/tpo",
        json={"email": email, "password": "StrongPass123", "name": "TPO User", "department_scope": []},
    )
    login = await client.post("/api/v1/auth/login", json={"email": email, "password": "StrongPass123"})
    return login.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_get_my_profile_returns_registration_fields(client):
    token = await _register_login_student(client)
    response = await client.get("/api/v1/students/me", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Profile Student"
    assert data["department"] == "CS"
    assert data["batch_year"] == 2026
    assert data["skills"] == []
    assert data["active_resume_id"] is None


@pytest.mark.asyncio
async def test_update_profile_partial_update_does_not_wipe_other_fields(client):
    token = await _register_login_student(client)
    await client.put(
        "/api/v1/students/me", headers=_auth_headers(token), json={"cgpa": 8.4, "skills": ["Python", "React"]}
    )
    response = await client.put(
        "/api/v1/students/me", headers=_auth_headers(token), json={"phone": "9999999999"}
    )
    assert response.status_code == 200
    data = response.json()
    # cgpa/skills from the first update must survive the second, unrelated update.
    assert data["cgpa"] == 8.4
    assert data["skills"] == ["Python", "React"]
    assert data["phone"] == "9999999999"


@pytest.mark.asyncio
async def test_profile_completeness_increases_as_fields_are_filled(client):
    token = await _register_login_student(client)
    before = await client.get("/api/v1/students/me", headers=_auth_headers(token))
    before_pct = before.json()["profile_completeness_pct"]

    after = await client.put(
        "/api/v1/students/me",
        headers=_auth_headers(token),
        json={
            "cgpa": 8.9,
            "phone": "9999999999",
            "linkedin_url": "https://linkedin.com/in/test",
            "github_url": "https://github.com/test",
            "skills": ["Python"],
        },
    )
    assert after.status_code == 200
    assert after.json()["profile_completeness_pct"] > before_pct


@pytest.mark.asyncio
async def test_tpo_cannot_access_student_profile_endpoints(client):
    token = await _register_login_tpo(client)
    get_response = await client.get("/api/v1/students/me", headers=_auth_headers(token))
    put_response = await client.put("/api/v1/students/me", headers=_auth_headers(token), json={"cgpa": 9.0})
    assert get_response.status_code == 403
    assert put_response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_request_is_rejected(client):
    response = await client.get("/api/v1/students/me")
    assert response.status_code == 401
