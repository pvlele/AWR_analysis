import csv

def ingest_ash(csv_file: str, base_metadata: dict):
    chunks = []

    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = (
                f"Time: {row['SAMPLE_TIME']}\n"
                f"Session: {row['SESSION_ID']}\n"
                f"SQL_ID: {row['SQL_ID']}\n"
                f"Wait Event: {row['EVENT']}\n"
                f"Blocking Session: {row['BLOCKING_SESSION']}"
            )

            chunks.append({
                "text": text,
                "metadata": {
                    **base_metadata,
                    "type": "ASH",
                    "sql_id": row.get("SQL_ID"),
                    "wait_event": row.get("EVENT"),
                    "blocking_session": row.get("BLOCKING_SESSION"),
                    "sample_time": row.get("SAMPLE_TIME")
                }
            })

    return chunks
