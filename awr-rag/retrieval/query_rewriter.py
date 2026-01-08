def rewrite(question: str) -> list[str]:
    return [
        f"Top timed events related to {question}",
        f"High CPU SQL related to {question}",
        f"IO bottlenecks related to {question}",
        f"Concurrency waits related to {question}"
    ]
