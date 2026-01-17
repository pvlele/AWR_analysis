from datetime import datetime
from utils.config import Config
import re

def create_chunks(sections: dict, metadata: dict) -> list:
    chunks = []
    chunk_size = Config.CHUNK_SIZE
    overlap = Config.CHUNK_OVERLAP

    for section, text in sections.items():
        text = text.strip()
        if not text:
            continue
            
        # Semantic splitting strategy
        # 1. Split by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_idx = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph exceeds chunk size, verify if we can split it further or just start a new chunk
            if len(current_chunk) + len(paragraph) + 2 > chunk_size:
                # If current chunk is not empty, save it
                if current_chunk:
                    chunks.append(_create_chunk_obj(current_chunk, section, chunk_idx, metadata))
                    chunk_idx += 1
                    # Start new chunk with overlap if needed (simple overlap not fully implemented for semantic yet, 
                    # but we keep context by not breaking paragraphs if possible)
                    # For strict overlap, we'd need a rolling window of words. 
                    # Here we prioritize keeping paragraphs intact.
                    current_chunk = ""

                # If the paragraph itself is larger than chunk size, we must split it by lines
                if len(paragraph) > chunk_size:
                    lines = paragraph.split('\n')
                    for line in lines:
                        if len(current_chunk) + len(line) + 1 > chunk_size:
                            if current_chunk:
                                chunks.append(_create_chunk_obj(current_chunk, section, chunk_idx, metadata))
                                chunk_idx += 1
                                current_chunk = ""
                            
                            # If line is still too big, brute force split (fallback to char split)
                            if len(line) > chunk_size:
                                start = 0
                                while start < len(line):
                                    end = start + chunk_size
                                    part = line[start:end]
                                    chunks.append(_create_chunk_obj(part, section, chunk_idx, metadata))
                                    chunk_idx += 1
                                    start += (chunk_size - overlap)
                                continue
                        
                        current_chunk += line + "\n"
                else:
                    current_chunk += paragraph + "\n\n"
            else:
                current_chunk += paragraph + "\n\n"
        
        # Add the last chunk
        if current_chunk:
            chunks.append(_create_chunk_obj(current_chunk, section, chunk_idx, metadata))

    return chunks

def _create_chunk_obj(text, section, idx, metadata):
    return {
        "text": text.strip(),
        "metadata": {
            **metadata,
            "section": section,
            "chunk_index": idx
        }
    }
