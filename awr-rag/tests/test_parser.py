from ingestion.awr_parser import load_awr
from ingestion.section_splitter import split_sections
from ingestion.chunker import create_chunks
import json

file_path = "data/raw/OLTP_AWR_5PM_6PM_27_JAN_2015.HTML"

print(f"Loading {file_path}...")
try:
    text = load_awr(file_path)
    print(f"Length of text: {len(text)}")
    print("First 500 chars:")
    print(text[:500])
    
    sections = split_sections(text)
    print(f"Found {len(sections)} sections.")
    
    chunks = create_chunks(sections, {"source": "test"})
    print(f"Created {len(chunks)} chunks.")
    
    # Find a chunk from 'SQL ordered by Reads'
    target_chunks = [c for c in chunks if "SQL ordered by Reads" in c['metadata'].get('section', '')]
    if target_chunks:
        print("\n--- Sample Chunk from SQL ordered by Reads ---")
        print(target_chunks[0]['text'][:500])
        print("...")
        if len(target_chunks) > 1:
             print("\n--- Second Chunk (checking header) ---")
             print(target_chunks[1]['text'][:500])
    else:
        print("No SQL ordered by Reads chunks found.")
        
except Exception as e:
    print(f"Error: {e}")
