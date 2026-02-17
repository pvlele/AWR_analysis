import time
import psutil
import threading
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasoning.analyzer import analyze
from ingestion.ingest import ingest_awr # Need chunks for context
from ingestion.chunker import create_chunks

load_dotenv()

# Configuration
TEST_MODELS = [
    "docker.io/ai/gemma3:4B",
    "docker.io/ai/llama3.1:8B-Q4_K_M"
    # "llama3:8b", # Add other models here if available
]
QUESTION = "Why was the database slow?"
TEST_FILE = "data/raw/OLTP_AWR_5PM_6PM_27_JAN_2015.HTML"

# Monitor Class
class ResourceMonitor(threading.Thread):
    def __init__(self, interval=0.1):
        super().__init__()
        self.interval = interval
        self.running = True
        self.cpu_usages = []
        self.memory_usages = []
        self.process = psutil.Process(os.getpid())

    def run(self):
        while self.running:
            try:
                # CPU percent since last call (system wide or process specific?)
                # Process specific is better
                self.cpu_usages.append(self.process.cpu_percent(interval=None))
                self.memory_usages.append(self.process.memory_info().rss / 1024 / 1024) # MB
                time.sleep(self.interval)
            except:
                break

    def stop(self):
        self.running = False


def run_benchmark():
    print(f"Loading data from {TEST_FILE}...")
    # Mock retrieval by just taking first X chunks to simulate context
    # We don't want to benchmark retrieval, just generation
    from ingestion.awr_parser import load_awr
    from ingestion.section_splitter import split_sections
    
    t0 = time.time()
    raw_text = load_awr(TEST_FILE)
    t1 = time.time()
    
    sections = split_sections(raw_text)
    t2 = time.time()
    
    chunks = create_chunks(sections, {"db": "TEST"})
    t3 = time.time()
    
    print(f"Ingestion Breakdown:")
    print(f"  Load:  {t1 - t0:.4f}s")
    print(f"  Split: {t2 - t1:.4f}s")
    print(f"  Chunk: {t3 - t2:.4f}s")
    print(f"  Total: {t3 - t0:.4f}s")
    print("-" * 80)
    
    # Use top 2 chunks as per our fix
    test_chunks = [{ "payload": c } for c in chunks[:2]] 
    # Wrap in object expected by analyzer if needed, but analyzer expects object with .payload['text']
    # Wait, analyzer does: chunk.payload["text"]
    # So we need objects that have .payload property or dict access?
    # Analyzer: chunk.payload["text"] -> chunk is an object from Qdrant client usually.
    # Let's create a simple mock class
    class MockChunk:
        def __init__(self, text):
            self.payload = {"text": text}
    
    mock_chunks = [MockChunk(c["text"]) for c in chunks[:2]]

    print("-" * 80)
    print(f"{'Model':<25} | {'Iter':<5} | {'Gen Time (s)':<12} | {'Peak RAM (MB)':<15} | {'Avg CPU (%)':<15}")
    print("-" * 80)

    for model in TEST_MODELS:
        print(f"Testing {model}...")
        for i in range(1, 3): # 2 Iterations
            monitor = ResourceMonitor()
            monitor.start()
            
            start_time = time.time()
            try:
                # First call process.cpu_percent() to initialize
                psutil.Process(os.getpid()).cpu_percent(interval=None)
                
                _ = analyze(QUESTION, mock_chunks, model_name=model)
                
                end_time = time.time()
                duration = end_time - start_time
                
                monitor.stop()
                monitor.join()

                peak_ram = max(monitor.memory_usages) if monitor.memory_usages else 0
                avg_cpu = sum(monitor.cpu_usages) / len(monitor.cpu_usages) if monitor.cpu_usages else 0
                
                print(f"{model:<25} | {i:<5} | {duration:<12.2f} | {peak_ram:<15.2f} | {avg_cpu:<15.2f}")

            except Exception as e:
                monitor.stop()
                print(f"{model:<25} | {i:<5} | FAILED: {str(e)}")
            
            # Small cooldown between runs
            time.sleep(2)

if __name__ == "__main__":
    run_benchmark()
