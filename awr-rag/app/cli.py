from dotenv import load_dotenv
load_dotenv()

import argparse
import sys
from ingestion.ingest import ingest_awr
from ingestion.metadata_parser import extract_metadata
from ingestion.awr_parser import load_awr
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.query_rewriter import rewrite
from retrieval.retriever import Retriever
from reasoning.analyzer import analyze
from utils.logger import setup_logger
from utils.config import Config
import datetime
import os

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AWR Analysis CLI")
    parser.add_argument(
        "--files", 
        nargs="+", 
        help="List of AWR HTML/Text files or directories to analyze. Defaults to 'data/raw' if not provided.", 
        required=False
    )
    parser.add_argument("-q", "--query", type=str, help="Analysis question", required=False)
    # Maintain backward compatibility if possible or just rely on args
    
    args = parser.parse_args()
    
    files = args.files
    question = args.query
    
    # 1. If no files provided, default to 'data/raw' directory
    if not files:
        default_dir = "data/raw"
        if os.path.isdir(default_dir):
            logger.info(f"No files specified. Scanning default directory: {default_dir}")
            files = [default_dir]
        else:
            logger.error(f"No files specified and default directory '{default_dir}' not found.")
            parser.print_help()
            sys.exit(1)

    # 2. Expand directories in 'files' list
    expanded_files = []
    for path in files:
        if os.path.isfile(path):
            expanded_files.append(path)
        elif os.path.isdir(path):
            logger.info(f"Scanning directory: {path}")
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if filename.lower().endswith(('.html', '.txt')):
                        full_path = os.path.join(root, filename)
                        expanded_files.append(full_path)
        else:
            logger.warning(f"Path not found: {path}")
            
    if not expanded_files:
        logger.error("No valid AWR files (html/txt) found.")
        sys.exit(1)
        
    logger.info(f"Found {len(expanded_files)} files to process: {expanded_files}")

    logger.info("Starting AWR Analysis...")
    try:
        # Iterate files and ingest individually
        all_chunks = []
        file_snapshot_map = [] # Track which file maps to which snapshot ID

        for idx, file_path in enumerate(expanded_files):
            try:
                logger.info(f"Ingesting {file_path}...")
                
                # 1. Load content for metadata extraction
                raw_text = load_awr(file_path)
                
                # 2. Extract metadata
                meta = extract_metadata(raw_text)
                
                # Generate a simple snapshot ID based on index or file name
                # Required for comparison identification
                snap_id = f"snap_{idx+1}"
                file_snapshot_map.append(snap_id)

                # 3. Map to expected keys
                ingest_meta = {
                    "db_name": meta.get("db_name", "UNKNOWN"),
                    "instance": "1",
                    "snap_begin": meta.get("start_time"),
                    "snap_end": meta.get("end_time"),
                    "snapshot_id": snap_id 
                }
                
                # 4. Ingest
                file_chunks = ingest_awr(file_path, ingest_meta)
                all_chunks.extend(file_chunks)
                
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")

        if not all_chunks:
            logger.error("No chunks generated from input files.")
            return

        chunks = all_chunks
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return

    try:
        embedder = Embedder()
        store = VectorStore(recreate=True)

        logger.info("Generating embeddings...")
        embeddings = embedder.embed([c["text"] for c in chunks])
        store.upsert(embeddings, chunks)
        
    except Exception as e:
        logger.error(f"Embedding/Storage failed: {e}")
        return

    # Interactive Loop
    if question:
        # Initial question if provided
        process_question(question, store, embedder, file_snapshot_map)
    else:
        print("\nReady for analysis. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            print("\n---------------------------------------------------------")
            user_input = input("Enter your question (or 'exit' to quit): ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
            
            if not user_input:
                continue

            process_question(user_input, store, embedder, file_snapshot_map)
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error processing question: {e}")

def process_question(question, store, embedder, snapshot_ids):
    queries = rewrite(question)
    logger.info(f"Generated queries: {queries}")

    retriever = Retriever(store)
    from retrieval.retriever import is_comparison_question
    
    # Check modification for comparison
    use_comparison = is_comparison_question(question) and len(snapshot_ids) == 2
    
    if use_comparison:
        print(f"Comparison mode detected between {snapshot_ids[0]} and {snapshot_ids[1]}")
        results = retriever.retrieve(queries, snapshot_ids=snapshot_ids)
        # Results is a dict
        
        print("\nRetrieved chunks for Comparison:")
        for sid, chunks in results.items():
            print(f"--- Snapshot {sid} ---")
            for r in chunks:
                print(f"- {r.payload['metadata']['section']}")
    else:
        results = retriever.retrieve(queries)
        print("\nRetrieved chunks:")
        for r in results:
            print("-", r.payload["metadata"]["section"])
            print(r.payload["text"][:300])
            print("-" * 60)

    # Calculate count for logging (list vs dict)
    count = 0
    if isinstance(results, dict):
        count = sum(len(v) for v in results.values())
    else:
        count = len(results)

    logger.info(f"Retrieved {count} chunks.")

    answer = analyze(question, results)
    
    save_report(answer, question)

def save_report(answer, question):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_content = f"""AWR Analysis Report
===================
Date: {timestamp}
Question: {question}
Model: {Config.MODEL_NAME}
Base URL: {Config.MODEL_BASE_URL}
API Path: {Config.MODEL_API_PATH}

Analysis:
---------
{answer}
"""

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file_path = os.path.join(output_dir, f"analysis_report_{file_timestamp}.txt")
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print("\nanalysis:\n")
    print(answer)
    print(f"\nReport saved to: {output_file_path}")

if __name__ == "__main__":
    main()
