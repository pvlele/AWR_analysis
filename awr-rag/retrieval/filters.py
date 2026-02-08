# Sections that actually matter for AWR performance analysis
IMPORTANT_SECTIONS = {
    "Top 10 Foreground Events": 3,
    "Top Timed Events": 3,
    "SQL ordered by Elapsed Time": 2,
    "SQL ordered by CPU Time": 2,
    "Load Profile": 1,
}

def is_relevant_section(section: str) -> bool:
    """
    Return True only if this section is important for performance diagnosis
    """
    for key in IMPORTANT_SECTIONS:
        if key.lower() in section.lower():
            return True
    return False


def section_weight(section: str) -> int:
    """
    Higher weight = higher priority in final context
    """
    for key, weight in IMPORTANT_SECTIONS.items():
        if key.lower() in section.lower():
            return weight
    return 0
