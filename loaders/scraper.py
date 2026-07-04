from __future__ import annotations
from time import time

from sympy import re

from model.article import Article
import requests
from pathlib import Path
from markdownify import markdownify as md



class Scraper:
    """
    A class to scrape articles from a given base URL.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def slugify(title: str) -> str:
        s = title.lower().strip()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"[\s_-]+", "-", s)
        return s[:80].strip("-") or "untitled"
    def from_html_to_md(self, html_content: str) -> str:
        """
        Convert HTML content to Markdown format.

        Args:
            html_content (str): The HTML content to convert.

        Returns:
            str: The converted Markdown content.
        """
        # Placeholder for actual HTML to Markdown conversion logic
        # You can use libraries like html2text or markdownify for this purpose
        return md(html_content, heading_style="ATX", code_language="")

    def scrape_articles(self) -> list[Article]:
        """
        Scrape articles from the base URL.

        Returns:
            list[Article]: A list of Article objects.
        """
        zendesk_url = f"{self.base_url}/api/v2/help_center/articles.json"
        
        params = dict(
            page=1,
            page_count=14,
            per_page=30,
        )
        
        articles = []
        while url and len(articles) < 30:
            resp = requests.get(zendesk_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            articles.extend([Article(**article) for article in data.get("articles", [])])
            url = data.get("next_page")
            params = None
            time.sleep(0.5)
            

        return articles[:30] if len(articles) > 30 else articles
    
    
    

