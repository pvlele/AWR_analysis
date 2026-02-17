from bs4 import BeautifulSoup
from pathlib import Path
from utils.text_utils import table_to_markdown

def load_awr(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".html":
        return _parse_html(path)
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


def _parse_html(path: Path) -> str:
    # Use lxml for speed and leniency
    text = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(text, "lxml")
    
    # Replace all tables with their pipe-separated text representation
    for table in soup.find_all("table"):
        markdown_table = table_to_markdown(table)
        # Add newlines to separate from surrounding text
        replacement = f"\n{markdown_table}\n"
        table.replace_with(soup.new_string(replacement))
        
    return soup.get_text(separator="\n")
