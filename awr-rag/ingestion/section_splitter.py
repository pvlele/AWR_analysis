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
        if any(sec in line for sec in AWR_SECTIONS):
            sections[current] = "\n".join(buffer)
            current = line
            buffer = []
        buffer.append(line)

    sections[current] = "\n".join(buffer)
    return sections
