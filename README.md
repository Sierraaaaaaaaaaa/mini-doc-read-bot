# Mini Doc Reader Bot

> **A small project for scraping Help Center articles and syncing them to an OpenAI Vector Store.**

---

## Project Structure

- `app/`: Main application logic coordinating scraping, diffing, and uploading.
- `config/`: Application configuration files and environment variables handling.
- `loaders/`: Data ingestion scripts, including the Zendesk help center web scraper.
- `model/`: Pydantic models for structuring data (e.g., `Article`, `State`).
- `uploader/`: OpenAI Vector Store integration for uploading and managing article documents.
- `data/`: Local storage for downloaded Markdown articles and the `state.json` file which tracks upload states and file hashes.

## Getting Started

### 1. Prerequisites

First, ensure you have your `.env` file set up in the root directory. You must at least provide your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-openai-api-key
```

### 2. Running Locally (Python)

Ensure your dependencies are installed. We recommend using a virtual environment.

```bash
pip install -r requirements.txt
```

You can run the entire pipeline (scraping, diffing, and uploading new/changed files) by running the main module from the root directory:

```bash
python -m app.main
```

*(Note: If you only want to test the scraper and save files locally without uploading them to OpenAI, you can run `python -m loaders.scraper` instead.)*

### 3. Running with Docker

You can easily run this as an isolated, one-off job using Docker.

**Build the image:**
```bash
docker build -t mini-doc-bot .
```

**Run the container:**
Make sure to mount your `data` volume so the `state.json` file persists across runs. This is crucial for the bot to remember which files it has already uploaded and only sync new or updated articles.

```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  mini-doc-bot
```

## How It Works

1. **Scrape**: Fetches articles from a Zendesk-backed Help Center and converts their HTML bodies to clean Markdown.
2. **Diff**: Compares the hashes of the downloaded articles against a local `state.json` to detect what has been added or updated since the last run.
3. **Upload**: Uses the OpenAI API to upload the changed files to a Vector Store and chunks them for Assistant search functionality, then updates `state.json` with the new file IDs.


## How to start asking

1. **Create an assitance with [OpenAI Playground UI](https://platform.openai.com/playground/assistants)**: You first need to create an assistance with OpenAI Playground with the instruction prompt:
```
  You are OptiBot, the customer-support bot for OptiSigns.com.
  • Tone: helpful, factual, concise.
  • Only answer using the uploaded docs.
  • Max 5 bullet points; else link to the doc.
  • Cite up to 3 "Article URL:" lines per reply.
```
2. **Add the vector store to the assistant**: After creating the assistant, go to the "Tool settings" and enable "File search". Then, attach the vector store created by this bot (it will be named `optisigns-support-docs`).
3. **Start chatting**: You can now ask questions in the Playground UI. The bot will query the synced vector store to fetch relevant articles and answer your questions concisely based on the document contents.

## Sample Run

![Sample Run](Sample%20run.png)
![Sample Log](sample%20log.png)

## Daily Jobs Log on Railway

![Daily Jobs log on railway](Daily%20Jobs%20log%20on%20railway.png)
