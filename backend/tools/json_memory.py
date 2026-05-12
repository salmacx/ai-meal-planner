import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JsonMemory:
    def __init__(self, path: str | None = None):
        default_path = Path(__file__).resolve().parents[1] / "data" / "user_memory.json"
        self.path = Path(path) if path else default_path

    def load(self) -> dict:
        if not self.path.exists():
            return {"diet": None, "allergies": [], "recent_meals": []}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {"diet": None, "allergies": [], "recent_meals": []}

    def save_preferences(self, diet: str | None, allergies: list[str]) -> dict:
        data = self.load()
        data["diet"] = diet
        data["allergies"] = allergies or []
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("memory_saved diet=%s allergies=%s", diet, len(allergies or []))
        return data

    def add_recent_meals(self, meal_names: list[str], limit: int = 25) -> None:
        data = self.load()
        recent = data.get("recent_meals", [])
        recent.extend(meal_names)
        deduped = []
        for name in recent[::-1]:
            if name not in deduped:
                deduped.append(name)
        data["recent_meals"] = deduped[:limit][::-1]
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info("memory_applied avoided_meals=%s", len(data['recent_meals']))