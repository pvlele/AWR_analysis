from bs4 import Tag, BeautifulSoup
from utils.config import Config

def table_to_markdown(table: Tag) -> str:
    """
    Convert HTML table to markdown-like text (pipe separated).
    Truncates long cell values based on Config.SQL_PREVIEW_LENGTH.
    """
    lines = []
    rows = table.find_all('tr')
    
    for tr in rows:
        cells = tr.find_all(['th', 'td'])
        if not cells:
            continue
            
        row_values = []
        truncated = False
        
        for cell in cells:
            text = cell.get_text(separator=" ", strip=True)
            text = text.replace("|", "/").replace("\n", " ")
            
            # Use configured length
            limit = getattr(Config, "SQL_PREVIEW_LENGTH", 100)
            if len(text) > limit:
                text = text[:limit] + "..."
                truncated = True
                
            row_values.append(text)
            
        # Join with pipes
        row_text = "| " + " | ".join(row_values) + " |"
        lines.append(row_text)
        
        if truncated:
             # This flag is used by chunker later; harmless for basic display but crucial for logic
             lines.append("HAS_FULL_SQL_FLAG: True")
             
    return "\n".join(lines)
