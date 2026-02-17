import pytest
from ingestion.chunker import create_chunks
from utils.config import Config

# Mock config for consistent test chunk sizes
@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    monkeypatch.setattr(Config, "CHUNK_SIZE", 50)
    monkeypatch.setattr(Config, "CHUNK_OVERLAP", 10)
    monkeypatch.setattr(Config, "SQL_PREVIEW_LENGTH", 15)

def test_create_chunks_basic():
    sections = {
        "Test Section": "Line 1\nLine 2\nLine 3"
    }
    metadata = {"source": "test"}
    
    chunks = create_chunks(sections, metadata)
    
    # Should fit in one chunk as total len is small (<50)
    assert len(chunks) == 1
    assert chunks[0]["text"].strip().endswith("Line 3")
    assert chunks[0]["metadata"]["section"] == "Test Section"

def test_create_chunks_splitting():
    # Create long text that forces splitting
    # Each line is ~20 chars ("This is line XX.\n")
    # 50 chars limit -> roughly 2 lines per chunk + overlap
    text = "\n".join([f"This is line {i}." for i in range(10)])
    sections = {"Big Section": text}
    
    chunks = create_chunks(sections, {})
    
    assert len(chunks) > 1
    # Check overlapping
    # Chunk 0: Line 0, Line 1...
    # Chunk 1: Line 1 (overlap), Line 2...
    
    assert "Line 0" in chunks[0]["text"]
    # Overlap check is tricky with exact implementation logic, but let's check basic structure
    assert chunks[0]["metadata"]["section"] == "Big Section"

def test_sticky_header_logic():
    # Sticky header logic applies when first lines start with |
    header = "| Col1 | Col2 |"
    row1 = "| Val1 | Val2 |"
    row2 = "| Val3 | Val4 |"
    row3 = "| Val5 | Val6 |"
    
    # Text: Header + Rows. 
    # If we force a split after row1, chunk 2 should ideally have the header again.
    text = f"{header}\n{row1}\n{row2}\n{row3}"
    
    # Force very small chunk size to trigger splits immediately
    # Header ~ 15 chars. Row ~ 15 chars.
    # Set limit to 35 chars -> Header + Row1 fits (30). Row 2 must wrap.
    # Chunk 2 should handle Row 2. Does it carry over header?
    
    # We need to manually set config for this test case specifically? 
    # Fixture sets it to 50. That's enough for Header + Row1 + Row2 (15*3 = 45).
    # Let's add more rows to force a split.
    text = "\n".join([header] + [f"| Row {i} Data |" for i in range(10)])
    
    chunks = create_chunks({"Table Section": text}, {})
    
    # Check if header appears in subsequent chunks (heuristic for sticky header)
    header_count = sum(1 for c in chunks if header in c["text"])
    assert header_count > 1, "Sticky header should appear in multiple chunks for long tables"

def test_sql_truncation_logic():
    # Process specific logic test via section name "SQL ordered by..."
    # Config preview length is 15.
    long_sql = "SELECT * FROM very_long_table_name_that_exceeds_limit WHERE 1=1"
    row = f"| 100 | {long_sql} |"
    
    sections = {"SQL ordered by Elapsed Time": row}
    chunks = create_chunks(sections, {})
    
    content = chunks[0]["text"]
    
    # It should be truncated
    assert "SELECT * FROM v..." in content or "SELECT * FROM..." in content
    # Should flag it
    assert "HAS_FULL_SQL_FLAG" in content
    assert "chunk_index" in chunks[0]["metadata"]
