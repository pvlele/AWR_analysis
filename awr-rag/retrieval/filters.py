IMPORTANT_SECTIONS = {
    "Top 10 Foreground Events": 3,
    "SQL ordered by Elapsed Time": 2,
    "SQL ordered by CPU Time": 2,
    "Load Profile": 1,
}

def is_relevant_section(section_name: str) -> bool:
    for key in IMPORTANT_SECTIONS:
        if key.lower() in section_name.lower():
            return True
    return False


def section_priority(section_name: str) -> int:
    for key, weight in IMPORTANT_SECTIONS.items():
        if key.lower() in section_name.lower():
            return weight
    return 0
