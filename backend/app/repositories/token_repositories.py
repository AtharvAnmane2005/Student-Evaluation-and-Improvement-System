from app.models.user import PasswordResetTokenInDB, RefreshTokenInDB
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshTokenInDB]):
    collection_name = "refresh_tokens"
    model = RefreshTokenInDB

    async def get_valid_by_hash(self, token_hash: str) -> RefreshTokenInDB | None:
        return await self.find_one({"token_hash": token_hash, "revoked": False})

    async def revoke(self, token_id: str) -> None:
        await self.update_by_id(token_id, {"revoked": True})

    async def revoke_all_for_user(self, user_id: str) -> None:
        await self.collection.update_many({"user_id": user_id}, {"$set": {"revoked": True}})


class PasswordResetTokenRepository(BaseRepository[PasswordResetTokenInDB]):
    collection_name = "password_reset_tokens"
    model = PasswordResetTokenInDB

    async def get_valid_by_hash(self, token_hash: str) -> PasswordResetTokenInDB | None:
        return await self.find_one({"token_hash": token_hash, "used": False})

    async def mark_used(self, token_id: str) -> None:
        await self.update_by_id(token_id, {"used": True})
