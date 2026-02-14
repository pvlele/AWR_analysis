from bs4 import BeautifulSoup
from pathlib import Path

def load_awr(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".html":
        return _parse_html(path)
    else:
        return path.read_text(encoding="utf-8", errors="ignore")


def _parse_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")
    return soup.get_text(separator="\n")
