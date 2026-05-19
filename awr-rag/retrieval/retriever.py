

from embeddings.embedder import Embedder

def detect_intent(question: str) -> str:
    q = question.lower()
    if "cpu" in q:
        return "CPU"
    if any(x in q for x in ["io", "read", "write", "disk", "i/o"]):
        return "IO"
    if any(x in q for x in ["slow", "latency", "wait", "hang", "stuck"]):
        return "SLOW"
    if any(x in q for x in ["sql", "query", "queries", "statement", "plan"]):
        return "SQL"
    return "GENERAL"


def is_comparison_question(question: str) -> bool:
    q = question.lower()
    triggers = ["compare", "difference", "vs", "between"]
    return any(t in q for t in triggers)

class Retriever:
    def __init__(self, store, max_chunks=6):
        self.store = store
        self.embedder = Embedder()
        self.max_chunks = max_chunks

    def retrieve(self, queries: list, filenames: list = None) -> list:
        # Detect intent from the queries
        combined_text = " ".join(queries)
        intent = detect_intent(combined_text)
        is_comparison = False
        
        # Check if we are in comparison mode
        if filenames and len(filenames) == 2:
            is_comparison = True

        if is_comparison:
            pass

        # Smart Retrieval Logic
        # 1. Semantic Search
        vectors = self.embedder.embed(queries)
        hits = []
        for v in vectors:
            h = self.store.search(v, limit=10)
            hits.extend(h)

        # 2. Hardcoded Critical Sections for Context
        critical_queries = []
        if intent in ["GENERAL", "SLOW"] and not is_comparison:
             critical_queries = [
                "Top 5 Timed Foreground Events",
                "Top Timed Events",
                "Load Profile",
                "Time Model Statistics",
                "Instance Efficiency Percentages"
            ]
        elif intent == "SQL":
             critical_queries = [
                "SQL ordered by Elapsed Time",
                "SQL ordered by CPU Time",
                "SQL ordered by Reads",
                "SQL ordered by User I/O Wait Time"
             ]

        if critical_queries:
            crit_vectors = self.embedder.embed(critical_queries)
            for cv in crit_vectors:
                 # Search with high limit to find effective matches
                 c_hits = self.store.search(cv, limit=5)
                 # Prioritize those that actually capture the section header
                 for ch in c_hits:
                     sec = ch.payload["metadata"]["section"]
                     # For SQL, we want chunks that ACTUALLY contain SQL data
                     if intent == "SQL" and "SQL" in sec:
                         # Insert at very top for SQL queries
                         hits.insert(0, ch)
                     elif ch.payload["metadata"]["chunk_index"] == 0:
                         checks = ["Top", "Timed", "Load Profile", "Foreground", "Time Model", "Efficiency", "HEADER"]
                         if any(c in sec for c in checks):
                            hits.append(ch) # Append for others

        # Deduplicate
        unique = {}
        # Simple dedupe by payload text
        for h in hits:
            txt = h.payload["text"]
            if txt not in unique:
                unique[txt] = h
        
        collected_unique = list(unique.values())
        
        filtered_results = []
        has_critical_section = False
        
        results_by_snapshot = {}
        if is_comparison:
             results_by_snapshot = {sid: [] for sid in filenames}

        for h in collected_unique:
            section = h.payload["metadata"]["section"]
            title = section.lower() if section else ""
            sid = h.payload["metadata"].get("filename")

            # Intent-based Restriction
            keep = True
            
            if intent == "CPU":
                if "cpu" not in title and "load profile" not in title and "sql" not in title:
                     keep = False
            elif intent == "IO":
                if not any(x in title for x in ["i/o", "read", "write", "tablespace", "file", "load profile", "sql"]):
                     keep = False
            elif intent == "SLOW":
                # We allow more sections for SLOW
                pass
            elif intent == "SQL":
                 # Prioritize SQL sections, but allow others if relevant (like Top Events to see if SQL is the cause)
                 if "sql" not in title and "top" not in title:
                      keep = False
            
            # Special case: Always keep SQL chunks if we ask for SQL
            if intent == "SQL" and "sql" in title:
                keep = True

            if keep:
                if is_comparison and sid:
                    if sid in results_by_snapshot:
                        results_by_snapshot[sid].append(h)
                else:
                    filtered_results.append(h)

        # Guardrails for single retrieval
        if not is_comparison:
            # If we didn't find critical sections via semantic search, we might struggle.
            # But we injected them above.
            return filtered_results[:self.max_chunks]

        # Guardrails for comparison
        final_comparison_results = {}
        for sid, chunks in results_by_snapshot.items():
             final_comparison_results[sid] = chunks[:self.max_chunks]

        return final_comparison_results
