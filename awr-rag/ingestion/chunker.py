import re
from bs4 import BeautifulSoup
from utils.config import Config

from utils.text_utils import table_to_markdown

def _clean_html_fragment(text: str) -> str:
    """
    Detects and converts HTML fragments to text/markdown if necessary.
    """
    if "<tr" not in text and "<table" not in text:
        return text
    
    try:
        # utilize lxml if available, else html.parser
        soup = BeautifulSoup(text, "lxml")
        if not soup.find("table"):
             return text # No tables, maybe just return text
             
        for table in soup.find_all("table"):
            markdown_table = table_to_markdown(table)
            replacement = f"\n{markdown_table}\n"
            table.replace_with(soup.new_string(replacement))
            
        return soup.get_text(separator="\n")
    except Exception:
        return text

def _process_sql_section(text: str, section_name: str) -> str:
    """
    detects SQL sections, parses entries to truncate full SQL text,
    and appends structured summary + flags.
    """
    if "SQL ordered by" not in section_name:
        return text

    # Pre-clean HTML if present
    text = _clean_html_fragment(text)

    lines = text.splitlines()
    new_lines = []
    current_sql_buffer = []
    first_sql_seen = False
    
    # Regex for SQL ID (13 chars alphanumeric words)
    sql_id_pattern = re.compile(r'\b[0-9a-z]{13}\b')

    for line in lines:
        # Check if line contains a SQL ID.
        match = sql_id_pattern.search(line)
        is_header = "SQL Id" in line or "-----" in line
        
        if "HAS_FULL_SQL_FLAG: True" in line:
             new_lines.append(line)
             continue

        if match and not is_header:
            # We found a metrics line with a SQL ID
            
            # Truncate long markdown lines (handled by awr_parser)
            if line.strip().startswith("|"):
                parts = line.split("|")
                new_parts = []
                truncated_in_line = False
                for p in parts:
                    if len(p) > Config.SQL_PREVIEW_LENGTH:
                        new_parts.append(p[:Config.SQL_PREVIEW_LENGTH] + "...")
                        truncated_in_line = True
                    else:
                        new_parts.append(p)
                line = "|".join(new_parts)
                if truncated_in_line:
                    new_lines.append("HAS_FULL_SQL_FLAG: True")
            
            # Flush existing buffer (previous SQL text)
            if current_sql_buffer:
                full_sql = "\n".join(current_sql_buffer).strip()
                if full_sql:
                    if len(full_sql) > Config.SQL_PREVIEW_LENGTH:
                        preview = full_sql[:Config.SQL_PREVIEW_LENGTH] + "..."
                        new_lines.append(f"SQL Preview: {preview}")
                        new_lines.append("HAS_FULL_SQL_FLAG: True")
                    else:
                        new_lines.append(f"SQL Preview: {full_sql}")
                current_sql_buffer = []

            first_sql_seen = True
            new_lines.append(line) # Preserve original metrics
            new_lines.append(f"SQL_ID: {match.group(0)}") # Explicit ID
            
        else:
            if first_sql_seen:
                # Accumulate SQL text, treating headers/separators carefully
                if "-----" in line:
                     # Separator might indicate end of sql text block or table structure
                     if current_sql_buffer:
                        full_sql = "\n".join(current_sql_buffer).strip()
                        if full_sql:
                            if len(full_sql) > Config.SQL_PREVIEW_LENGTH:
                                preview = full_sql[:Config.SQL_PREVIEW_LENGTH] + "..."
                                new_lines.append(f"SQL Preview: {preview}")
                                new_lines.append("HAS_FULL_SQL_FLAG: True")
                            else:
                                new_lines.append(f"SQL Preview: {full_sql}")
                        current_sql_buffer = []
                     new_lines.append(line)
                else:
                    current_sql_buffer.append(line)
            else:
                new_lines.append(line)

    # Final flush
    if current_sql_buffer:
        full_sql = "\n".join(current_sql_buffer).strip()
        if full_sql:
            if len(full_sql) > Config.SQL_PREVIEW_LENGTH:
                preview = full_sql[:Config.SQL_PREVIEW_LENGTH] + "..."
                new_lines.append(f"SQL Preview: {preview}")
                new_lines.append("HAS_FULL_SQL_FLAG: True")
            else:
                new_lines.append(f"SQL Preview: {full_sql}")

    return "\n".join(new_lines)

def _finalize_chunk(chunk_text: str, metadata: dict) -> tuple:
    """
    Parses chunk text to extract metadata and clean up internal flags.
    """
    lines = chunk_text.splitlines()
    final_lines = []
    has_full_sql = False
    previews = []
    
    for line in lines:
        if "HAS_FULL_SQL_FLAG: True" in line:
            has_full_sql = True
            continue 
        
        if line.startswith("SQL Preview:"):
            # Extract content, minimal split to avoid issues with colons in SQL
            try:
                content = line.split("SQL Preview:", 1)[1].strip()
                if content:
                    previews.append(content)
            except IndexError:
                pass
        
        final_lines.append(line)
        
    final_text = "\n".join(final_lines)
    
    # Remove more than 2 consecutive newlines
    final_text = re.sub(r'\n{3,}', '\n\n', final_text)
    
    # Prepend section name to text for better retrieval context
    section_name = metadata.get("section", "")
    if section_name:
        final_text = f"Section: {section_name}\n\n{final_text}"
    
    new_metadata = metadata.copy()
    if has_full_sql:
        new_metadata["has_full_sql"] = True
    if previews:
        new_metadata["sql_preview"] = previews
        
    return final_text, new_metadata

def create_chunks(sections: dict, metadata: dict) -> list:
    chunks = []
    MAX_CHAR = Config.CHUNK_SIZE
    OVERLAP = Config.CHUNK_OVERLAP

    for section, text in sections.items():
        # Pre-process SQL sections to optimize tokens
        text = _process_sql_section(text, section)
        
        text = text.strip()
        if not text:
            continue
            
        # Check if text is small enough
        if len(text) <= MAX_CHAR:
             final_text, final_meta = _finalize_chunk(text, {
                **metadata,
                "section": section,
                "chunk_index": 0,
                "type": "AWR"
             })
             chunks.append({
                "text": final_text,
                "metadata": final_meta
            })
             continue

        # Pre-process lines to split overly long lines
        raw_lines = text.splitlines()
        lines = []
        for l in raw_lines:
            if len(l) > MAX_CHAR:
                # Split huge line into chunks of MAX_CHAR
                for k in range(0, len(l), MAX_CHAR):
                    lines.append(l[k:k+MAX_CHAR])
            else:
                lines.append(l)
        
def _create_chunks_from_lines(lines: list, section: str, metadata: dict, max_char: int, overlap: int) -> list:
    chunks = []
    
    # Identify Sticky Header (first line starting with |)
    sticky_header = None
    for l in lines[:10]:
        if l.strip().startswith("|"):
            sticky_header = l
            break
            
    current_chunk_lines = []
    current_char_count = 0
    chunk_idx = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_len = len(line) + 1 # +1 for newline
        
        # If adding this line exceeds max char, flush current chunk
        if current_char_count + line_len > max_char:
            # Need to flush if we have content
            if current_chunk_lines:
                chunk_text = "\n".join(current_chunk_lines)
                final_text, final_meta = _finalize_chunk(chunk_text, {
                    **metadata,
                    "section": section,
                    "chunk_index": chunk_idx,
                    "type": "AWR"
                })
                chunks.append({
                    "text": final_text,
                    "metadata": final_meta
                })
                chunk_idx += 1
                
                # Calculate overlap by backtracking
                backtrack_chars = 0
                overlap_lines = []
                j = i - 1
                while j >= 0:
                    l = lines[j]
                    l_len = len(l) + 1
                    
                    if backtrack_chars + l_len > overlap and backtrack_chars > 0:
                        break

                    backtrack_chars += l_len
                    overlap_lines.insert(0, l)
                    
                    if backtrack_chars >= overlap:
                        break
                    j -= 1
                
                current_chunk_lines = list(overlap_lines)
                current_char_count = backtrack_chars
                
                # Add sticky header if applicable
                if sticky_header:
                    if sticky_header not in current_chunk_lines:
                        h_len = len(sticky_header) + 1
                        if current_char_count + h_len <= max_char:
                            current_chunk_lines.insert(0, sticky_header)
                            current_char_count += h_len

                # Handle overflow on single line
                if current_char_count + line_len > max_char:
                     # Retry with just sticky header + line
                     current_chunk_lines = []
                     current_char_count = 0
                     if sticky_header:
                         current_chunk_lines.append(sticky_header)
                         current_char_count += len(sticky_header) + 1
                     
                     if current_char_count + line_len > max_char:
                         pass
                
                current_chunk_lines.append(line)
                current_char_count += line_len
                i += 1
            else:
                current_chunk_lines.append(line)
                current_char_count += line_len
                i += 1
        else:
            current_chunk_lines.append(line)
            current_char_count += line_len
            i += 1
            
    # Flush the last chunk
    if current_chunk_lines:
        chunk_text = "\n".join(current_chunk_lines)
        final_text, final_meta = _finalize_chunk(chunk_text, {
            **metadata,
            "section": section,
            "chunk_index": chunk_idx,
            "type": "AWR"
        })
        chunks.append({
            "text": final_text,
            "metadata": final_meta
        })

    return chunks

def create_chunks(sections: dict, metadata: dict) -> list:
    chunks = []
    MAX_CHAR = Config.CHUNK_SIZE
    OVERLAP = Config.CHUNK_OVERLAP

    for section, text in sections.items():
        # Pre-process SQL sections to optimize tokens
        text = _process_sql_section(text, section)
        
        text = text.strip()
        if not text:
            continue
            
        # Check if text is small enough
        if len(text) <= MAX_CHAR:
             final_text, final_meta = _finalize_chunk(text, {
                **metadata,
                "section": section,
                "chunk_index": 0,
                "type": "AWR"
             })
             chunks.append({
                "text": final_text,
                "metadata": final_meta
            })
             continue

        # Pre-process lines to split overly long lines
        raw_lines = text.splitlines()
        lines = []
        for l in raw_lines:
            if len(l) > MAX_CHAR:
                # Split huge line into chunks of MAX_CHAR
                for k in range(0, len(l), MAX_CHAR):
                    lines.append(l[k:k+MAX_CHAR])
            else:
                lines.append(l)
        
        # Use helper for complex loop
        section_chunks = _create_chunks_from_lines(lines, section, metadata, MAX_CHAR, OVERLAP)
        chunks.extend(section_chunks)

    return chunks
