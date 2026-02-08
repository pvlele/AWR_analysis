from dotenv import load_dotenv
load_dotenv()

import argparse
import sys
from ingestion.ingest import ingest_awr
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
        # Pass list of files
        chunks = ingest_awr(expanded_files)
        if not chunks:
            logger.error("No chunks generated from input files.")
            return
            
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
        process_question(question, store, embedder)
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

            process_question(user_input, store, embedder)
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error processing question: {e}")

def process_question(question, store, embedder):
    queries = rewrite(question)
    logger.info(f"Generated queries: {queries}")

    retriever = Retriever(store, embedder)
    results = retriever.retrieve(queries)
    logger.info(f"Retrieved {len(results)} chunks.")

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

Analysis:
---------
{answer}
"""

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file_path = os.path.join(output_dir, f"analysis_report_{file_timestamp}.txt")
    
    with open(output_file_path, "w") as f:
        f.write(output_content)

    print("\nanalysis:\n")
    print(answer)
    print(f"\nReport saved to: {output_file_path}")

if __name__ == "__main__":
    main()
