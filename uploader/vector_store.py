from __future__ import annotations

import math
from typing import Any, Optional

from openai import OpenAI

from config.settings import Settings
from model.state import State

CHUNK_SIZE_TOKENS = 1000
CHUNK_OVERLAP_TOKENS = 200


class OpenAIVectorStore:
    def __init__(self, client: Optional[OpenAI] = None, vector_store_id: Optional[str] = None):
        if Settings.OPENAI_API_KEY is None:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        self.client = client or OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.vector_store_id = vector_store_id
        self.ensure_vector_store(self.vector_store_id)

    def ensure_vector_store(self, vector_store_id: Optional[str]) -> str:
        if vector_store_id:
            try:
                self.client.vector_stores.retrieve(vector_store_id)
                self.vector_store_id = vector_store_id
                return vector_store_id
            except Exception:
                pass
        vs = self.client.vector_stores.create(name="optisigns-support-docs")
        self.vector_store_id = vs.id
        return vs.id

    def estimate_chunks(self, filepath: str) -> int:
        text = open(filepath, encoding="utf-8").read()
        approx_tokens = max(1, len(text) // 4)
        step = CHUNK_SIZE_TOKENS - CHUNK_OVERLAP_TOKENS
        return max(1, math.ceil(approx_tokens / step))

    def upload_file_to_vector_store(self, filepath: str, attributes: dict) -> str:
        with open(filepath, "rb") as f:
            file_obj = self.client.files.create(file=f, purpose="assistants")

        self.client.vector_stores.files.create_and_poll(
            vector_store_id=self.vector_store_id,
            file_id=file_obj.id,
            attributes=attributes,
            chunking_strategy={
                "type": "static",
                "static": {
                    "max_chunk_size_tokens": CHUNK_SIZE_TOKENS,
                    "chunk_overlap_tokens": CHUNK_OVERLAP_TOKENS,
                },
            },
        )
        return file_obj.id

    def delete_file_from_vector_store(self, file_id: str) -> None:
        try:
            self.client.vector_stores.files.delete(
                vector_store_id=self.vector_store_id, file_id=file_id
            )
        except Exception:
            pass
        try:
            self.client.files.delete(file_id)
        except Exception:
            pass

    def sync_files(self, diff: dict[str, list[dict]], state: State) -> dict[str, int]:
        articles_delta = {}
        total_chunks_estimate = 0

        for item in diff["added"] + diff["updated"]:
            key = str(item["id"])
            old = state._state.get("articles", {}).get(key)  # still needs read access -- add a getter if you want this fully private too
            if old and old.get("file_id"):
                self.delete_file_from_vector_store(old["file_id"])

            attributes = {"id": item["id"], "slug": item["slug"], "url": item["url"], "title": item["title"], "hash": item["hash"]}
            file_id = self.upload_file_to_vector_store(item["path"], attributes)
            total_chunks_estimate += self.estimate_chunks(item["path"])
            articles_delta[key] = {**attributes, "file_id": file_id}

        state.update_articles(articles_delta)
        return {
            "added": len(diff["added"]), "updated": len(diff["updated"]), "skipped": len(diff["skipped"]),
            "files_uploaded": len(diff["added"]) + len(diff["updated"]), "estimated_chunks": total_chunks_estimate,
        }