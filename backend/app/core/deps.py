"""
Reusable FastAPI dependencies: current-user extraction and RBAC guards.

get_current_user now does a full DB round-trip (Phase 4) so a deactivated
or deleted account is rejected immediately, not just once its access token
happens to expire.
"""
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    role: str
    email: str


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise credentials_exception from exc

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return CurrentUser(id=user.id, role=user.role.value, email=user.email)


def require_role(*allowed_roles: str):
    """
    Usage: @router.get(..., dependencies=[Depends(require_role("admin", "tpo"))])
    """

    async def _checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not permitted to access this resource.",
            )
        return current_user

    return _checker
