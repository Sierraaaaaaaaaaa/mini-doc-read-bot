from __future__ import annotations

from pydantic import BaseModel

class Article(BaseModel):
    id: str
    slug: str
    url: str
    created_at: str
    updated_at: str
    title: str
    hash: str
    path: str