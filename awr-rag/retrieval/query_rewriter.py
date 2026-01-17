from utils.logger import setup_logger

logger = setup_logger(__name__)

class QueryRewriter:
    def rewrite(self, question: str) -> list[str]:
        # Ideally, this could look up templates based on domain categorization
        # or use an LLM. For now, we keep it deterministic but structured.
        templates = [
            "Top timed events related to {question}",
            "High CPU SQL related to {question}",
            "IO bottlenecks related to {question}",
            "Concurrency waits related to {question}"
        ]
        
        queries = [t.format(question=question) for t in templates]
        logger.info(f"Generated {len(queries)} variations for query: {question}")
        return queries

# def rewrite(question: str) -> list[str]:
#     q = question.lower()
#     queries = []

#     queries.append("Top timed events and wait events")

#     if "cpu" in q:
#         queries.append("High CPU SQL statements")
#     if "io" in q or "read" in q:
#         queries.append("IO related waits and disk reads")
#     if "slow" in q or "performance" in q:
#         queries.append("SQL ordered by elapsed time")
#     if "lock" in q or "contention" in q:
#         queries.append("Concurrency and blocking waits")

#     return list(set(queries))


# Simple functional adapter if needed for backward compatibility or direct import
def rewrite(question: str) -> list[str]:
    return QueryRewriter().rewrite(question)
