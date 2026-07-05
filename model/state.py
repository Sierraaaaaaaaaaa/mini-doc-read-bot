from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STATE_PATH = Path(__file__).parent.parent / "data" / "state.json"

class State:
    def __init__(self):
        self._state: dict[str, Any] = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if not STATE_PATH.exists():
            return {"vector_store_id": None, "assistant_id": None, "articles": {}}
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))


    def save(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(self._state, indent=2), encoding="utf-8")
    
    def set_vector_store_id(self, vector_store_id: str) -> None:
        self._state["vector_store_id"] = vector_store_id

    def set_assistant_id(self, assistant_id: str) -> None:
        self._state["assistant_id"] = assistant_id

    def diff_manifest(self, new_manifest: list[dict[str, Any]]) -> dict[str, list[dict]]:
        current_articles = self._state.get("articles", {})
        added, updated, skipped = [], [], []

        for item in new_manifest:
            key = str(item["id"])  
            prev = current_articles.get(key)
            if prev is None:
                added.append(item)
            elif prev.get("hash") != item["hash"]:
                updated.append(item)
            else:
                skipped.append(item)

        return {"added": added, "updated": updated, "skipped": skipped}

    def update_articles(self, articles_delta: dict[str, dict]) -> None:
        """Called by sync_files AFTER a successful upload, to merge in the
        new hash/file_id/etc. for each added/updated article."""
        self._state.setdefault("articles", {}).update(articles_delta)