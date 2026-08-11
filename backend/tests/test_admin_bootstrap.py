import pytest

from app.models.user import AdminRegisterRequest
from app.services.auth_service import AuthError, AuthService


@pytest.mark.asyncio
async def test_register_admin_creates_user_and_admin_profile(mock_mongo):
    service = AuthService(mock_mongo)
    user = await service.register_admin(
        AdminRegisterRequest(email="bootstrap.admin@college.edu", password="StrongPass123", name="Placement Admin")
    )

    assert user.role == "admin"
    assert user.email == "bootstrap.admin@college.edu"

    admin_profile = await service.admins.get_by_user_id(user.id)
    assert admin_profile is not None
    assert admin_profile.name == "Placement Admin"


@pytest.mark.asyncio
async def test_register_admin_rejects_duplicate_email(mock_mongo):
    service = AuthService(mock_mongo)
    payload = AdminRegisterRequest(email="dup.admin@college.edu", password="StrongPass123", name="Admin One")
    await service.register_admin(payload)

    with pytest.raises(AuthError) as exc_info:
        await service.register_admin(payload)
    assert exc_info.value.status_code == 409


@pytest.mark.asyncio
async def test_created_admin_can_log_in_over_http(client):
    from app.core import database as db_module

    service = AuthService(db_module.mongodb.db)
    await service.register_admin(
        AdminRegisterRequest(email="loginflow.admin@college.edu", password="StrongPass123", name="Admin Login Test")
    )

    response = await client.post(
        "/api/v1/auth/login", json={"email": "loginflow.admin@college.edu", "password": "StrongPass123"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["role"] == "admin"
