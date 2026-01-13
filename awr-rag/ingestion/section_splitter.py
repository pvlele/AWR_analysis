import re

AWR_SECTIONS = [
    "Load Profile",
    "Instance Efficiency Percentages",
    "Top 10 Foreground Events by Total Wait Time",
    "SQL ordered by Elapsed Time",
    "SQL ordered by CPU Time",
    "IO Statistics",
    "Memory Statistics"
]

def split_sections(awr_text: str) -> dict:
    sections = {}
    current = "HEADER"
    buffer = []

    for line in awr_text.splitlines():
        line = line.strip()
        # Check if the line *starts with* one of the section headers.
        # This is safer than 'in' which matches substrings anywhere.
        matched_section = next((sec for sec in AWR_SECTIONS if line.startswith(sec)), None)

        if matched_section:
            sections[current] = "\n".join(buffer)
            current = matched_section
            buffer = []

        buffer.append(line)

    sections[current] = "\n".join(buffer)
    return sections
