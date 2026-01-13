import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from ingestion.awr_parser import load_awr
from ingestion.section_splitter import split_sections

class TestAWRParser(unittest.TestCase):
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_load_awr_text_file(self, mock_read_text, mock_exists):
        mock_exists.return_value = True
        mock_read_text.return_value = "Content"

        result = load_awr("test.txt")
        self.assertEqual(result, "Content")
        mock_read_text.assert_called_with(encoding="utf-8", errors="replace")

    @patch("pathlib.Path.exists")
    def test_load_awr_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            load_awr("nonexistent.txt")

    @patch("pathlib.Path.exists")
    @patch("ingestion.awr_parser._parse_html")
    def test_load_awr_html_file(self, mock_parse_html, mock_exists):
        mock_exists.return_value = True
        mock_parse_html.return_value = "Parsed HTML"

        result = load_awr("test.html")
        self.assertEqual(result, "Parsed HTML")
        mock_parse_html.assert_called()

class TestSectionSplitter(unittest.TestCase):
    def test_split_sections(self):
        text = """HEADER
Some text
Load Profile
Stats here
Instance Efficiency Percentages
More stats
Memory Statistics
End"""
        sections = split_sections(text)
        self.assertIn("HEADER", sections)
        self.assertIn("Load Profile", sections)
        self.assertIn("Instance Efficiency Percentages", sections)
        self.assertIn("Memory Statistics", sections)

        self.assertEqual(sections["HEADER"].strip(), "HEADER\nSome text")
        # The splitter includes the header line in the section content
        self.assertEqual(sections["Load Profile"].strip(), "Load Profile\nStats here")

    def test_split_sections_partial_match(self):
        # This checks that our new logic DOES NOT split on partial matches inside sentences
        text = """HEADER
This line contains Load Profile but is not a header
"""
        sections = split_sections(text)
        self.assertIn("HEADER", sections)
        self.assertNotIn("Load Profile", sections)
        self.assertIn("This line contains Load Profile but is not a header", sections["HEADER"])

if __name__ == "__main__":
    unittest.main()
