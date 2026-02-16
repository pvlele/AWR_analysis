from bs4 import BeautifulSoup, Tag
from pathlib import Path

def load_awr(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".html":
        return _parse_html(path)
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


def _table_to_markdown(table: Tag) -> str:
    lines = []
    rows = table.find_all('tr')
    
    for tr in rows:
        cells = tr.find_all(['th', 'td'])
        if not cells:
            continue
            
        # Extract text and clean it
        row_values = []
        for cell in cells:
            text = cell.get_text(separator=" ", strip=True)
            # Escape pipes to avoid breaking table structure, replace newlines
            text = text.replace("|", "/").replace("\n", " ")
            row_values.append(text)
            
        # Join with pipes
        row_text = "| " + " | ".join(row_values) + " |"
        lines.append(row_text)
        
    return "\n".join(lines)


def _parse_html(path: Path) -> str:
    # Use lxml for speed and leniency
    text = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(text, "lxml")
    
    # Replace all tables with their pipe-separated text representation
    for table in soup.find_all("table"):
        markdown_table = _table_to_markdown(table)
        # Add newlines to separate from surrounding text
        replacement = f"\n{markdown_table}\n"
        table.replace_with(soup.new_string(replacement))
        
    return soup.get_text(separator="\n")
