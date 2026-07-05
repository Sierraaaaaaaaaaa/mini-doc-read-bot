from __future__ import annotations


from dataclasses import asdict
import time

import hashlib
import re
from typing import Optional, Any
from model.article import Article
import requests
from pathlib import Path
from markdownify import markdownify as md
from config.settings import Settings


class Scraper:
    """Pulls Help Center articles from a Zendesk-backed site and writes
    each one to disk as a clean Markdown file."""

    def __init__(self, base_url: str = Settings.DEFAULT_BASE_URL, articles_dir: Optional[Path] = None):
        self.base_url = base_url.rstrip("/")
        self.articles_dir = articles_dir or Path(__file__).parent.parent / "data" / "articles"


    @staticmethod
    def slugify(title: str) -> str:
        s = title.lower().strip()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s_-]+", "-", s)
        return s[:80].strip("-") or "untitled"

    @staticmethod
    def html_to_markdown(html: str) -> str:
        if not html:
            return ""
        return md(html, heading_style="ATX", bullets="-", code_language="").strip()

    @staticmethod
    def content_hash(markdown_body: str) -> str:
        """Hash of just the article body -- used to detect real content
        changes between runs (see state.py)."""
        return hashlib.sha256(markdown_body.encode("utf-8")).hexdigest()


    def fetch_all_articles(self, min_count: int = 30, per_page: int = 100) -> list[dict]:
        """Paginate through the Zendesk Help Center Articles endpoint until
        we have at least min_count articles (or the site runs out of pages)."""
        articles: list[dict] = []
        url = f"{self.base_url}/api/v2/help_center/articles.json"
        params: Optional[dict] = {
            "per_page": per_page,
            "sort_by": "position",
            "sort_order": "asc",
        }

        while url:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            articles.extend(data.get("articles", []))

            url = data.get("next_page")
            params = None  

            if len(articles) >= min_count and not url:
                break
            if url:
                time.sleep(0.25)  

        return articles[:31] if len(articles) > 31 else articles

    @classmethod
    def build_markdown_file(cls, article: dict) -> tuple[str, str, str]:
        """Returns (slug, full_markdown_text, content_hash)."""
        title = article.get("title") or f"Untitled-{article['id']}"
        slug = cls.slugify(title)
        body_md = cls.html_to_markdown(article.get("body", ""))

        full_text = f"# {title}\n\nArticle URL: {article.get('html_url', '')}\n\n{body_md}\n"
        return slug, full_text, cls.content_hash(body_md)

    def scrape_to_markdown(self, min_count: int = 30) -> list[Article]:
        """Scrapes articles and writes them to disk as <slug>.md.
        Returns a manifest of Article entries."""
        self.articles_dir.mkdir(parents=True, exist_ok=True)
        articles = self.fetch_all_articles(min_count=min_count)

        manifest: list[Article] = []
        seen_slugs: dict[str, int] = {}

        for article in articles:
            slug, full_text, h = self.build_markdown_file(article)

            # de-dupe slug collisions (e.g. two articles both titled "Getting Started")
            if slug in seen_slugs:
                seen_slugs[slug] += 1
                slug = f"{slug}-{seen_slugs[slug]}"
            else:
                seen_slugs[slug] = 0

            path = self.articles_dir / f"{slug}.md"
            path.write_text(full_text, encoding="utf-8")

            manifest.append(
                Article(
                    id=str(article["id"]),
                    slug=slug,
                    title=article.get("title", ""),
                    url=article.get("html_url", ""),
                    created_at=article.get("created_at", ""),
                    updated_at=article.get("updated_at", ""),
                    hash=h,
                    path=str(path),
                )
            )

        return manifest


# ---- module-level convenience wrapper ----
# Keeps `from scraper import scrape_to_markdown` working unchanged for
# main.py / state.py / uploader.py, which expect a list[dict].
def scrape_to_markdown(min_count: int = 30) -> list[dict]:
    scraper = Scraper()
    records = scraper.scrape_to_markdown(min_count=min_count)
    return [r.model_dump() for r in records]


if __name__ == "__main__":
    result = scrape_to_markdown(min_count=30)
    print(f"Scraped {len(result)} articles into {Scraper().articles_dir}")
