import unittest
import sys
import os

# Add project root to sys.path to ensure modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.chunker import create_chunks
from utils.config import Config

class TestChunker(unittest.TestCase):
    def setUp(self):
        # Override config for testing to force splits
        Config.CHUNK_SIZE = 50
        Config.CHUNK_OVERLAP = 10

    def test_semantic_split_paragraphs(self):
        text = "Para1 is small.\n\nPara2 is also small but separate.\n\nPara3 is here."
        sections = {"test_section": text}
        metadata = {"source": "test"}
        
        chunks = create_chunks(sections, metadata)
        
        # Expect roughly 3 chunks, respecting paragraphs if they fit
        # "Para1 is small." (15 chars) -> fits
        # "Para2 is also small but separate." (33 chars) -> fits
        # "Para3 is here." (14 chars) -> fits
        
        self.assertEqual(len(chunks), 3)
        self.assertIn("Para1 is small.", chunks[0]["text"])
        self.assertIn("Para2 is also small", chunks[1]["text"])

    def test_large_chunk_split(self):
        # A para larger than chunk size (50)
        text = "This is a very long paragraph that definitely exceeds the fifty character limit we set for testing purposes."
        sections = {"test_section": text}
        metadata = {"source": "test"}
        
        chunks = create_chunks(sections, metadata)
        
        # Should be split
        self.assertTrue(len(chunks) > 1)
        # Check first chunk is not empty
        self.assertTrue(len(chunks[0]["text"]) > 0)
        # Check total content length is roughly preserved (ignoring overlap duplication)
        reconstructed = "".join([c["text"] for c in chunks])
        self.assertIn("This is a very long", reconstructed)

if __name__ == '__main__':
    unittest.main()
