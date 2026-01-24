from ingestion.awr_parser import load_awr
from ingestion.section_splitter import split_sections
from ingestion.chunker import create_chunks
from ingestion.metadata_parser import extract_metadata
import json
import os
from typing import List, Union

def ingest_awr(file_paths: Union[str, List[str]], metadata_override: dict = None):
    if isinstance(file_paths, str):
        file_paths = [file_paths]
        
    all_chunks = []
    
    for file_path in file_paths:
        print(f"Processing {file_path}...")
        try:
            raw_text = load_awr(file_path)
            
            # Extract metadata from content
            extracted_metadata = extract_metadata(raw_text)
            
            # Merge with override if provided, override takes precedence
            file_metadata = extracted_metadata.copy()
            if metadata_override:
                file_metadata.update(metadata_override)
                
            # Add source filename
            file_metadata["source_file"] = os.path.basename(file_path)
            
            sections = split_sections(raw_text)
            chunks = create_chunks(sections, file_metadata)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Save all chunks for debug/caching
    # Ensure directory exists
    os.makedirs("data/processed", exist_ok=True)
    
    with open("data/processed/awr_chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)

    return all_chunks
