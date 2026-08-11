"""
One-time (or occasional) CLI script to create an admin account.

There is deliberately no public `POST /auth/register/admin` route — unlike
student/TPO registration, admin accounts should never be self-service over
a public API. This script talks to MongoDB directly, reusing the same
AuthService.register_admin() logic (and therefore the same password
hashing / validation) that a route would use, without exposing one.

Usage (from backend/, with the venv active):
    python -m scripts.create_admin
    python -m scripts.create_admin --email admin@college.edu --name "Placement Admin"

If --password is omitted, you'll be prompted (hidden input, via getpass) —
preferred over passing it on the command line, which would leak into shell
history.
"""
import argparse
import asyncio
import getpass
import sys

from pydantic import ValidationError

from app.core.database import close_mongo_connection, connect_to_mongo, get_database
from app.models.user import AdminRegisterRequest
from app.services.auth_service import AuthError, AuthService


async def _create_admin(email: str, password: str, name: str) -> None:
    await connect_to_mongo()
    try:
        db = get_database()
        service = AuthService(db)
        payload = AdminRegisterRequest(email=email, password=password, name=name)
        user = await service.register_admin(payload)
        print(f"\nAdmin account created: {user.email} (id: {user.id})")
        print("You can now log in at /login with this email and password.")
    except AuthError as exc:
        print(f"\nError: {exc.message}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as exc:
        print(f"\nInvalid input:\n{exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        await close_mongo_connection()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an admin account for PLACER.")
    parser.add_argument("--email", help="Admin email (prompted if omitted)")
    parser.add_argument("--name", help="Admin display name (prompted if omitted)")
    parser.add_argument(
        "--password",
        help="Admin password (prompted with hidden input if omitted — preferred, avoids shell history)",
    )
    args = parser.parse_args()

    email = args.email or input("Admin email: ").strip()
    name = args.name or input("Admin name: ").strip()
    password = args.password or getpass.getpass("Admin password (min 8 characters): ")

    asyncio.run(_create_admin(email, password, name))


if __name__ == "__main__":
    main()
