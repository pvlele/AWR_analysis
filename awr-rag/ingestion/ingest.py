from ingestion.awr_parser import load_awr
from ingestion.section_splitter import split_sections
from ingestion.chunker import create_chunks
import json

def ingest_awr(file_path: str, metadata: dict):
    raw_text = load_awr(file_path)
    sections = split_sections(raw_text)
    chunks = create_chunks(sections, metadata)

    with open("data/processed/awr_chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)

    return chunks
