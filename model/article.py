from __future__ import annotations

from pydantic import BaseModel

class Article(BaseModel):
    id: str
    url: str
    html_url: str
    author_id: int
    comments_disabled: bool
    draft: bool
    created_at: str
    updated_at: str
    name: str
    title: str
    source_locale: str
    locale: str
    body: str