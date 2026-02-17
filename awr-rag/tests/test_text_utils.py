import pytest
from bs4 import BeautifulSoup, Tag
from utils.text_utils import table_to_markdown
from utils.config import Config

@pytest.fixture
def mock_html_table():
    html = """
    <table>
        <tr><th>Header1</th><th>Header2</th></tr>
        <tr><td>Data1</td><td>Data2</td></tr>
        <tr><td>LongDataThatShouldBeTruncatedButWaitLetsMakeItLongerThanLimit</td><td>Short</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('table')

def test_table_to_markdown_basic(mock_html_table):
    # Test basic conversion
    markdown = table_to_markdown(mock_html_table)
    
    assert "| Header1 | Header2 |" in markdown
    assert "| Data1 | Data2 |" in markdown

def test_table_to_markdown_truncation():
    # Setup - Override config for testing
    original_limit = Config.SQL_PREVIEW_LENGTH
    Config.SQL_PREVIEW_LENGTH = 10
    
    try:
        html = """
        <table>
            <tr><td>123456789012345</td></tr>
        </table>
        """
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        
        markdown = table_to_markdown(table)
        
        # Should be truncated to 10 chars + ...
        # 1234567890 (10 chars) ... -> "1234567890..."
        assert "1234567890..." in markdown
        assert "HAS_FULL_SQL_FLAG: True" in markdown
        
    finally:
        # Cleanup
        Config.SQL_PREVIEW_LENGTH = original_limit

def test_table_to_markdown_special_chars():
    html = """
    <table>
        <tr><td>Pipe|Char</td><td>New\nLine</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    
    markdown = table_to_markdown(table)
    
    # Pipe should be replaced by slash, newline by space
    assert "Pipe/Char" in markdown
    assert "New Line" in markdown
