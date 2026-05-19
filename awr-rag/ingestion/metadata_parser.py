import re
from typing import Dict, Optional

def extract_metadata(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts metadata from AWR markdown/text content.
    Tries to find 'DB Name' and 'Snapshot' information.
    """
    metadata = {
        "db_name": None,
        "instance": None,
        "start_time": None,
        "end_time": None
    }
    
    # 1. Extract DB Name and Inst num
    # Match: | DB Name | DB Id | Instance | Inst num | ...
    #        | HHMLPROD | ... | MYINST | 1 | ...
    db_name_match = re.search(r"\|\s*DB Name\s*\|[^\n]*\n\|\s*([^\|]+?)\s*\|(?:\s*[^\|]+\s*\|){2}\s*([^\|]+?)\s*\|", text)
    if db_name_match:
        metadata["db_name"] = db_name_match.group(1).strip()
        metadata["instance"] = db_name_match.group(2).strip()
    else:
        # Fallback for plain text format
        # DB Name         DB Id    Instance     Inst Num
        # ------------ ----------- ------------ --------
        # PROD_DB      1234567890 PROD_INST           1
        db_name_match_txt = re.search(r"Host Name:\s*(\S+)", text)
        if db_name_match_txt:
            metadata["db_name"] = db_name_match_txt.group(1).strip()
            
        inst_num_match_txt = re.search(r"Inst[ance]*\s*[Nn]um[ber]*\s*:\s*(\S+)", text)
        if inst_num_match_txt:
            metadata["instance"] = inst_num_match_txt.group(1).strip()
        else:
            instance_match_txt = re.search(r"Instance:\s*(\S+)", text)
            if instance_match_txt:
                metadata["instance"] = instance_match_txt.group(1).strip()
            else:
                # Another text format
                alt_match = re.search(r"DB Name\s+DB Id\s+Instance\s+Inst Num[^\n]*\n[^\n]*\n\s*(\S+)\s+\S+\s+\S+\s+(\S+)", text)
                if alt_match:
                    if not metadata["db_name"]:
                        metadata["db_name"] = alt_match.group(1).strip()
                    metadata["instance"] = alt_match.group(2).strip()
            
    # 2. Extract Snapshot Time / Interval
    # Match: | Begin Snap: | 80340 |
    begin_snap_match = re.search(r"\|\s*Begin Snap:\s*\|\s*(\d+)\s*\|", text)
    if begin_snap_match:
        metadata["start_time"] = begin_snap_match.group(1).strip()
        
    end_snap_match = re.search(r"\|\s*End Snap:\s*\|\s*(\d+)\s*\|", text)
    if end_snap_match:
        metadata["end_time"] = end_snap_match.group(1).strip()
        
    return metadata
