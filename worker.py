import collections
from utils import clean_text

def worker_main(worker_id, task_queue, result_queue):
    print(f"[Worker {worker_id}] Starting initialization...")
    local_counter = collections.Counter()
    processed_files = 0

    while True:
        task = task_queue.get()
        
        if task is None:
            print(f"[Worker {worker_id}] Received stop signal. Files processed: {processed_files}")
            break

        file_path = task
        print(f"[Worker {worker_id}] Processing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                words = clean_text(text)
                local_counter.update(words)
                processed_files += 1
        except Exception as e:
            print(f"[Worker {worker_id}] Error reading {file_path}: {e}")

    # Wysyłanie danych do koordynatora
    print(f"[Worker {worker_id}] Sending aggregated results to coordinator...")
    result_queue.put({
        "worker_id": worker_id,
        "counter": local_counter
    })
    print(f"[Worker {worker_id}] Process terminated cleanly.")