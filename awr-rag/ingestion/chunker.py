from datetime import datetime

def create_chunks(sections: dict, metadata: dict) -> list:
    chunks = []

    for section, text in sections.items():
        text = text.strip()
        if not text:
            continue
            
        # Split text into chunks of max 1500 chars with 150 chars overlap
        chunk_size = 1500
        overlap = 150
        
        if len(text) <= chunk_size:
            chunks.append({
                "text": text,
                "metadata": {
                    **metadata,
                    "section": section,
                    "chunk_index": 0
                }
            })
        else:
            start = 0
            idx = 0
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end]
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "section": section,
                        "chunk_index": idx
                    }
                })
                
                if end >= len(text):
                    break
                    
                start += (chunk_size - overlap)
                idx += 1
                
    return chunks
