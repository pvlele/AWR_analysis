from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import shutil
import os
from typing import List
import logging

# App logic imports
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

logger = setup_logger("webapp")

app = FastAPI(title="AWR RAG Analysis")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Ensure temp directory for uploads exists
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

# Global state for interactive mode
store = None
embedder = None
processed_files_list = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shutdown")
async def shutdown():
    import signal
    import os
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "Server shutting down..."}

@app.post("/ingest")
async def ingest_files(files: List[UploadFile] = File(...)):
    global store, embedder, processed_files_list
    saved_file_paths = []
    
    try:
        # 1. Save uploaded files
        for file in files:
            file_path = os.path.join(Config.UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append(file_path)
        
        logger.info(f"Processing {len(saved_file_paths)} files provided by user.")

        # 2. Ingest
        all_chunks = []
        for idx, file_path in enumerate(saved_file_paths):
            try:
                raw_text = load_awr(file_path)
                meta = extract_metadata(raw_text)
                
                # Generate a unique snapshot_id for comparison later
                filename = os.path.basename(file_path)
                
                ingest_meta = {
                    "db_name": meta.get("db_name") or "UNKNOWN",
                    "instance": meta.get("instance") or "1",
                    "snap_begin": meta.get("start_time"),
                    "snap_end": meta.get("end_time"),
                    "filename": filename
                }
                
                file_chunks = ingest_awr(file_path, ingest_meta)
                all_chunks.extend(file_chunks)
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")

        chunks = all_chunks
        if not chunks:
             return JSONResponse(status_code=400, content={"error": "No valid content found in uploaded files."})

        # 3. Embed & Store
        # Initialize embedder and store if not exists, or recreate for new ingestion
        embedder = Embedder()
        store = VectorStore(recreate=True) # Recreate for new upload batch
        
        logger.info("Generating embeddings...")
        embeddings = embedder.embed([c["text"] for c in chunks])
        store.upsert(embeddings, chunks)
        
        processed_files_list = [os.path.basename(p) for p in saved_file_paths]
        
        return {"message": f"Successfully processed {len(processed_files_list)} files.", "files": processed_files_list}

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/config")
async def get_config():
    from utils.config import Config
    return {
        "models": Config.AVAILABLE_MODELS,
        "default_model": Config.MODEL_NAME
    }

@app.post("/chat")
async def chat(query: str = Form(...), model: str = Form(None)):
    global store, embedder
    
    if not store or not embedder:
        return JSONResponse(status_code=400, content={"error": "No data ingested. Please upload files first."})

    try:
        # 4. Retrieval
        queries = rewrite(query)
        retriever = Retriever(store)
        from retrieval.retriever import is_comparison_question
        
        # Enable comparison mode if comparing exactly 2 files
        use_comparison = is_comparison_question(query) and len(processed_files_list) == 2
        
        if use_comparison:
            logger.info(f"Comparison mode activated for {processed_files_list}")
            results = retriever.retrieve(queries, filenames=processed_files_list)
        else:
            results = retriever.retrieve(queries)
        
        # 5. Analysis
        # Use provided model or default
        answer = analyze(query, results, model_name=model)
        
        return {
            "question": query,
            "answer": answer,
            "processed_files": processed_files_list,
            "model_used": model
        }

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

def run():
    uvicorn.run("app.web:app", host="0.0.0.0", port=8088, reload=True)

if __name__ == "__main__":
    run()
