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
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.query_rewriter import rewrite
from retrieval.retriever import Retriever
from reasoning.analyzer import analyze
from utils.logger import setup_logger

logger = setup_logger("webapp")

app = FastAPI(title="AWR RAG Analysis")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Ensure temp directory for uploads exists
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shutdown")
async def shutdown():
    import signal
    import os
    os.kill(os.getpid(), signal.SIGINT)
    return {"message": "Server shutting down..."}

@app.post("/analyze")
async def analyze_awr(
    query: str = Form(...),
    files: List[UploadFile] = File(...)
):
    saved_file_paths = []
    
    try:
        # 1. Save uploaded files
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_file_paths.append(file_path)
        
        logger.info(f"Processing {len(saved_file_paths)} files provided by user.")

        # 2. Ingest
        chunks = ingest_awr(saved_file_paths)
        if not chunks:
             return JSONResponse(status_code=400, content={"error": "No valid content found in uploaded files."})

        # 3. Embed & Store
        embedder = Embedder()
        store = VectorStore()
        
        # Note: in a real app you might want to use a persistent collection or session ID
        # For now, we overwrite/add to the default collection
        embeddings = embedder.embed([c["text"] for c in chunks])
        store.upsert(embeddings, chunks)
        
        # 4. Retrieval
        queries = rewrite(query)
        retriever = Retriever(store, embedder)
        results = retriever.retrieve(queries)
        
        # 5. Analysis
        answer = analyze(query, results)
        
        return {
            "question": query,
            "answer": answer,
            "processed_files": [os.path.basename(p) for p in saved_file_paths]
        }

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        # Cleanup uploaded files? Optional. For now keep them for debug.
        pass

def run():
    uvicorn.run("app.web:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
