from typing import Optional, Dict, Any
from server.db.db import get_db


class UsersRepo:
    def __init__(self):
        self._col = get_db()["users"]

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self._col.find_one({"email": email})

    def create_user(self, username: str, email: str, password_hash: str) -> str:
        r = self._col.insert_one(
            {"username": username, "email": email, "password": password_hash}
        )
        return str(r.inserted_id)