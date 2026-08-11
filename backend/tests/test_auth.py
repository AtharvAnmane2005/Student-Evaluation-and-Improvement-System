import pytest


async def _register_and_login(client, email="student@college.edu", password="StrongPass123"):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": email,
            "password": password,
            "name": "Test Student",
            "department": "Computer Science",
            "batch_year": 2026,
        },
    )
    login_res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return login_res


@pytest.mark.asyncio
async def test_register_student_success(client):
    response = await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": "new.student@college.edu",
            "password": "StrongPass123",
            "name": "Jane Doe",
            "department": "Electronics",
            "batch_year": 2027,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.student@college.edu"
    assert body["role"] == "student"
    assert "password" not in body
    assert "password_hash" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client):
    payload = {
        "email": "dup@college.edu",
        "password": "StrongPass123",
        "name": "Dup User",
        "department": "CS",
        "batch_year": 2026,
    }
    first = await client.post("/api/v1/auth/register/student", json=payload)
    second = await client.post("/api/v1/auth/register/student", json=payload)
    assert first.status_code == 201
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_login_success_sets_refresh_cookie_and_returns_access_token(client):
    response = await _register_and_login(client)
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["user"]["role"] == "student"
    assert "placer_refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": "wrongpass@college.edu",
            "password": "StrongPass123",
            "name": "T",
            "department": "CS",
            "batch_year": 2026,
        },
    )
    response = await client.post(
        "/api/v1/auth/login", json={"email": "wrongpass@college.edu", "password": "WrongOne123"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_requires_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_valid_token(client):
    login_res = await _register_and_login(client)
    access_token = login_res.json()["access_token"]

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["role"] == "student"


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_old_cookie_becomes_invalid(client):
    login_res = await _register_and_login(client, email="refresh@college.edu")
    refresh_cookie = login_res.cookies["placer_refresh_token"]

    client.cookies.set("placer_refresh_token", refresh_cookie)
    first_refresh = await client.post("/api/v1/auth/refresh")
    assert first_refresh.status_code == 200
    assert "access_token" in first_refresh.json()

    # Reusing the now-rotated-out cookie should fail.
    client.cookies.set("placer_refresh_token", refresh_cookie)
    second_refresh = await client.post("/api/v1/auth/refresh")
    assert second_refresh.status_code == 401


@pytest.mark.asyncio
async def test_logout_clears_session(client):
    login_res = await _register_and_login(client, email="logout@college.edu")
    refresh_cookie = login_res.cookies["placer_refresh_token"]
    client.cookies.set("placer_refresh_token", refresh_cookie)

    logout_res = await client.post("/api/v1/auth/logout")
    assert logout_res.status_code == 204

    client.cookies.set("placer_refresh_token", refresh_cookie)
    refresh_after_logout = await client.post("/api/v1/auth/refresh")
    assert refresh_after_logout.status_code == 401


@pytest.mark.asyncio
async def test_forgot_password_always_returns_202_even_for_unknown_email(client):
    response = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody@college.edu"})
    assert response.status_code == 202


# ---------------------------------------------------------------------
# Google Sign-In — token verification is mocked so tests never call
# Google's real servers.
# ---------------------------------------------------------------------
class _FakeGooglePayload:
    def __init__(self, sub, email, email_verified=True, name="Google User"):
        self.sub = sub
        self.email = email
        self.email_verified = email_verified
        self.name = name


@pytest.mark.asyncio
async def test_google_signup_creates_new_student_account(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.auth_service.verify_google_token",
        lambda credential: _FakeGooglePayload(sub="google-uid-1", email="newgoogle@gmail.com"),
    )

    response = await client.post(
        "/api/v1/auth/google", json={"credential": "fake-id-token", "role": "student"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "newgoogle@gmail.com"
    assert body["user"]["role"] == "student"
    assert body["profile_incomplete"] is True  # department/batch_year unknown from Google


@pytest.mark.asyncio
async def test_google_login_existing_account_no_profile_incomplete_flag(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.auth_service.verify_google_token",
        lambda credential: _FakeGooglePayload(sub="google-uid-2", email="returning@gmail.com"),
    )

    first = await client.post("/api/v1/auth/google", json={"credential": "t1", "role": "student"})
    second = await client.post("/api/v1/auth/google", json={"credential": "t2", "role": "student"})

    assert first.json()["profile_incomplete"] is True
    assert second.json()["profile_incomplete"] is False
    assert first.json()["user"]["id"] == second.json()["user"]["id"]


@pytest.mark.asyncio
async def test_google_signin_blocked_for_existing_local_account(client, monkeypatch):
    await client.post(
        "/api/v1/auth/register/student",
        json={
            "email": "local.user@college.edu",
            "password": "StrongPass123",
            "name": "Local User",
            "department": "CS",
            "batch_year": 2026,
        },
    )
    monkeypatch.setattr(
        "app.services.auth_service.verify_google_token",
        lambda credential: _FakeGooglePayload(sub="google-uid-3", email="local.user@college.edu"),
    )

    response = await client.post(
        "/api/v1/auth/google", json={"credential": "fake-id-token", "role": "student"}
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_google_signin_rejects_unverified_email(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.auth_service.verify_google_token",
        lambda credential: _FakeGooglePayload(
            sub="google-uid-4", email="unverified@gmail.com", email_verified=False
        ),
    )

    response = await client.post(
        "/api/v1/auth/google", json={"credential": "fake-id-token", "role": "student"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_local_password_login_rejected_for_google_only_account(client, monkeypatch):
    monkeypatch.setattr(
        "app.services.auth_service.verify_google_token",
        lambda credential: _FakeGooglePayload(sub="google-uid-5", email="googleonly@gmail.com"),
    )
    await client.post("/api/v1/auth/google", json={"credential": "t1", "role": "student"})

    response = await client.post(
        "/api/v1/auth/login", json={"email": "googleonly@gmail.com", "password": "anything123"}
    )
    assert response.status_code == 401
