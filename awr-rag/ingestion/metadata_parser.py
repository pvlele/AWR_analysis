from bs4 import BeautifulSoup
import re
from typing import Dict, Optional

def extract_metadata(html_content: str) -> Dict[str, Optional[str]]:
    """
    Extracts metadata from AWR HTML content.
    Tries to find 'DB Name' and 'Snapshot' information.
    """
    soup = BeautifulSoup(html_content, "lxml")
    metadata = {}
    
    # Heuristic: AWR reports often have a table with DB Name, DB Id, etc. at the top.
    # We look for standard labels.
    
    # 1. Extract DB Name
    # Table headers often contain "DB Name"
    db_name = None
    # Search for a th or td containing "DB Name"
    db_name_tag = soup.find(lambda tag: tag.name in ["th", "td"] and "DB Name" in tag.get_text())
    if db_name_tag:
        # The value is usually in the next row or same row next cell
        # Standard AWR top table structure check
        # Case 1: Header row, Data row
        # Find the index of the column
        pass # Simplified for now, just trying to find text near it or in a table
        
        parent_row = db_name_tag.find_parent("tr")
        if parent_row:
            # Check if it's a header row, then get the value from the next tr
            siblings = parent_row.find_next_siblings("tr")
            if siblings:
                 # Assuming the structure is Header -> Data
                 # Need to find index of db_name_tag
                 cells = parent_row.find_all(["th", "td"])
                 try:
                     index = cells.index(db_name_tag)
                     data_row = siblings[0]
                     data_cells = data_row.find_all(["th", "td"])
                     if index < len(data_cells):
                         db_name = data_cells[index].get_text(strip=True)
                 except ValueError:
                     pass

    metadata["db_name"] = db_name

    # 2. Extract Snapshot Time / Interval
    # Look for "Snapshot Beginning" or similar, or just "Snap Time"
    # AWR Header: Snap Id | Snap Time | Sessions | Curs/Sess ...
    
    # We will look for "Snap Time" in the general text or table if specific parsing fails,
    # but let's try to grab the first and last extracted timestamp if we can parsing the summary table.
    
    # Simplified approach: Look for a pattern like "DD-Mon-YY HH:MM:SS"
    # Or find the "Snapshot" table.
    
    # Let's try to find the "Report Summary" or similar text which often contains the range.
    
    # Fallback/General: Just try to find the first valid date string in the document? No, too risky.
    
    # Attempt to find the "Snap Id" table
    snap_table_header = soup.find(lambda tag: tag.name in ["th", "td"] and "Snap Id" in tag.get_text())
    start_time = None
    end_time = None
    
    if snap_table_header:
         parent_row = snap_table_header.find_parent("tr")
         # Usually: Snap Id | Snap Time | ...
         # The next rows are the start and end snapshots
         if parent_row:
             siblings = parent_row.find_next_siblings("tr")
             if len(siblings) >= 2:
                 # Begin Snap
                 start_row = siblings[0]
                 start_cells = start_row.find_all(["td", "th"])
                 if len(start_cells) > 1:
                     start_time = start_cells[1].get_text(strip=True)
                 
                 # End Snap
                 end_row = siblings[1] # Usually specifically Begin and End rows
                 end_cells = end_row.find_all(["td", "th"])
                 if len(end_cells) > 1:
                     end_time = end_cells[1].get_text(strip=True)
                     
    metadata["start_time"] = start_time
    metadata["end_time"] = end_time
    
    return metadata
