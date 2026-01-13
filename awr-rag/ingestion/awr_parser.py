from bs4 import BeautifulSoup
from pathlib import Path

def load_awr(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        if path.suffix.lower() == ".html":
            return _parse_html(path)
        else:
            return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise RuntimeError(f"Failed to load AWR file: {e}")


def _parse_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(errors="ignore"), "lxml")
    return soup.get_text(separator="\n")
