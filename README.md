# Mini doc render

> **An small project of scheduling web article rendering**

---

## Project structure

- `app/`: Main application logic.
- `loaders/`: Data ingestion scripts, including the Zendesk help center web scraper.
- `model/`: Pydantic models for structuring data (e.g., Articles, State).
- `config/`: Application configuration files.

## Getting Started

### 1. Scraping Articles

Before running the main application, you need to pull down the article data. The scraper fetches Help Center articles and saves them locally as clean Markdown files.

From the root directory of the project, run:

```bash
# Ensure your dependencies are installed
python -m loaders.scraper
```

This will download the articles and store them in the `loaders/data/articles/` directory.
