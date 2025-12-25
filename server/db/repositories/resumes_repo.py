from typing import Optional, Dict, Any, List
from bson import ObjectId
from server.db.db import get_db


class ResumesRepo:
    def __init__(self):
        self._col = get_db()["parsed_resumes"]

    def create(self, doc: Dict[str, Any]) -> str:
        r = self._col.insert_one(doc)
        return str(r.inserted_id)

    def find_one_for_user(self, resume_id: str, email: str) -> Optional[Dict[str, Any]]:
        return self._col.find_one({"_id": ObjectId(resume_id), "uploaded_by": email})

    def list_for_user(self, email: str) -> List[Dict[str, Any]]:
        return list(self._col.find({"uploaded_by": email}).sort("uploaded_at", -1))