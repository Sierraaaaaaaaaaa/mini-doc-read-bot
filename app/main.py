from __future__ import annotations

import logging
import sys


from config.settings import Settings
from model.state import State
from model.article import Article
from loaders.scraper import scrape_to_markdown
from uploader.vector_store import OpenAIVectorStore



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

log = logging.getLogger("optibot-job")


def main() -> None: 
    log.info("Starting the job...")
    manifest = scrape_to_markdown()
    state = State()
    diff = state.diff_manifest(manifest)
    log.info(
        "Diff -> added: %d, updated: %d, skipped: %d",
        len(diff["added"]),
        len(diff["updated"]),
        len(diff["skipped"]),
    )
    
    if not diff["added"] and not diff["updated"]:
        log.info("No new or updated articles to upload. Exiting.")
        return
    
    client = OpenAIVectorStore(vector_store_id=state._state.get("vector_store_id"))
    state.set_vector_store_id(client.vector_store_id)
    state.save()  # persist the ID immediately, before any upload attempt
    upload_stats = client.sync_files(diff, state)
    log.info(
        "Upload stats -> added: %d, updated: %d, skipped: %d, files_uploaded: %d, estimated_chunks: %d",
        upload_stats["added"],
        upload_stats["updated"],
        upload_stats["skipped"],
        upload_stats["files_uploaded"],
        upload_stats["estimated_chunks"],
    )
    state.save()
    
    
if __name__ == "__main__":
    main()