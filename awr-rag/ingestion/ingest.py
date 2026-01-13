from ingestion.awr_parser import load_awr
from ingestion.section_splitter import split_sections
from ingestion.chunker import create_chunks
from utils.logging import setup_logger
import json
import os

logger = setup_logger()

def ingest_awr(file_path: str, metadata: dict, output_path: str = None):
    logger.info(f"Starting ingestion for {file_path}")

    raw_text = load_awr(file_path)
    logger.info(f"Loaded {len(raw_text)} characters from file")

    sections = split_sections(raw_text)
    logger.info(f"Split into {len(sections)} sections")

    chunks = create_chunks(sections, metadata)
    logger.info(f"Created {len(chunks)} chunks")

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(chunks, f, indent=2)
        logger.info(f"Saved chunks to {output_path}")

    return chunks
