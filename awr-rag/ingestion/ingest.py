

from ingestion.awr_parser import load_awr
from ingestion.section_splitter import split_sections
from ingestion.chunker import create_chunks

import json
import os

def ingest_awr(file_path: str, metadata: dict):
    raw_text = load_awr(file_path)
    sections = split_sections(raw_text)

    # Ensure required metadata is present (pass-through)
    chunks = create_chunks(
        sections,
        metadata={
            "db_name": metadata.get("db_name", "UNKNOWN"),
            "instance": metadata.get("instance", 1),
            "snap_begin": metadata.get("snap_begin"),
            "snap_end": metadata.get("snap_end"),
            "snapshot_id": metadata.get("snapshot_id", "UNKNOWN"), # Unique ID for comparison
        }
    )

    # Save chunks for debug/verification
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/awr_chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)

    return chunks
