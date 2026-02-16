from utils.logger import setup_logger

logger = setup_logger(__name__)

# class QueryRewriter:
#     def rewrite(self, question: str) -> list[str]:
#         # Ideally, this could look up templates based on domain categorization
#         # or use an LLM. For now, we keep it deterministic but structured.
#         templates = [
#             "Top timed events related to {question}",
#             "High CPU SQL related to {question}",
#             "IO bottlenecks related to {question}",
#             "Concurrency waits related to {question}"
#         ]
        
#         queries = [t.format(question=question) for t in templates]
#         logger.info(f"Generated {len(queries)} variations for query: {question}")
#         return queries

# # Simple functional adapter if needed for backward compatibility or direct import


def rewrite(question: str) -> list[str]:
    q = question.lower()
    queries = [question]  # Start with original

    # Add specific domain queries based on keywords
    if "cpu" in q:
        queries.append("SQL ordered by CPU Time")
    if any(x in q for x in ["io", "read", "write", "disk"]):
        queries.append("SQL ordered by User I/O Wait Time")
    if any(x in q for x in ["slow", "performance", "wait", "latency"]):
        queries.append("Top Timed Events")
        queries.append("SQL ordered by Elapsed Time")
    if any(x in q for x in ["lock", "contention", "block"]):
        queries.append("Segments by Row Lock Waits")

    # Dedup while preserving order
    seen = set()
    ordered_queries = []
    for qry in queries:
        if qry not in seen:
            ordered_queries.append(qry)
            seen.add(qry)

    return ordered_queries

# def rewrite(question: str) -> list[str]:
#    return QueryRewriter().rewrite(question)