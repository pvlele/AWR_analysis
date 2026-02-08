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
    queries = []

    # Always check top waits
    queries.append("Top wait events and DB time")

    if "cpu" in q:
        queries.append("SQL ordered by CPU time")
    if "io" in q or "read" in q or "write" in q:
        queries.append("IO waits and disk reads")
    if "slow" in q or "performance" in q:
        queries.append("SQL ordered by elapsed time")
    if "lock" in q or "contention" in q or "block" in q:
        queries.append("enq TX row lock contention")

    return list(set(queries))

# def rewrite(question: str) -> list[str]:
#    return QueryRewriter().rewrite(question)