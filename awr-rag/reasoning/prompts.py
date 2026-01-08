SYSTEM_PROMPT = """
You are an Oracle performance expert.
Use only provided AWR data.
Cite metrics and sections.
Do not speculate.
"""

USER_TEMPLATE = """
Analyze the AWR data and answer:
{question}

Evidence:
{context}
"""
