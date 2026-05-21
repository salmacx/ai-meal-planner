from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient

class MongoMemory:

    def __init__(self, mongo_uri: str | None = None, db_name: str = "ai_meal_planner"):
        self.collection = None

        print("MONGO URI:", mongo_uri)

        if not mongo_uri:
            print("NO MONGO URI")
            return

        try:
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=3000,
                tlsAllowInvalidCertificates=True
            )
            client.admin.command("ping")
            self.collection = client[db_name]["meal_plans"]
            print("Mongo connected")
        except Exception as e:
            print("Mongo connection failed:", e)
            self.collection = None

    def save_plan(self, user_id, request, generated_plan):
        if self.collection is None:
            print("NO COLLECTION (not saving)")
            return

        print("SAVING PLAN for user:", user_id)

        self.collection.insert_one({
            "user_id": user_id or "default_user",
            "request": request,
            "generated_plan": generated_plan,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        print("Mongo connected:", self.collection)

    def get_recent_plans(self, user_id: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
            if self.collection is None:
                return []
            query = {"user_id": user_id} if user_id else {}
            cursor = self.collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)