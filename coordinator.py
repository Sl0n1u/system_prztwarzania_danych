import os
import time
import multiprocessing as mp
from collections import Counter
from worker import worker_main

def run_parallel_system(directory_path, num_workers):
    print(f"[Coordinator] Rozpoczynam przetwarzanie w '{directory_path}' z {num_workers} workerami.")
    
    if not os.path.exists(directory_path):
        print(f"[Coordinator] Blad: Folder '{directory_path}' nie istnieje.")
        return 0, 0, 0

    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.txt')]
    if not files:
        print("[Coordinator] Brak plikow do przetworzenia.")
        return 0, 0, 0

    task_queue = mp.Queue()
    result_queue = mp.Queue()

    # Start pomiaru calkowitego
    start_time = time.time()

    processes = []
    for i in range(num_workers):
        p = mp.Process(target=worker_main, args=(i, task_queue, result_queue))
        processes.append(p)
        p.start()

    # MAP: Rozsylanie zadan i praca workerow
    map_start = time.time()
    
    for file_path in files:
        task_queue.put(file_path)
    for _ in range(num_workers):
        task_queue.put(None)

    results_list = []
    while len(results_list) < num_workers:
        results_list.append(result_queue.get())
        
    map_end = time.time()
    map_time = map_end - map_start

    # REDUCE: Agregacja zebranych wynikow
    reduce_start = time.time()
    
    final_counter = Counter()
    for result in results_list:
        final_counter.update(result["counter"])
        print(f"[Coordinator] Zagregowano wyniki od Workera {result['worker_id']}")
        
    reduce_end = time.time()
    reduce_time = reduce_end - reduce_start


    for p in processes:
        p.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print("\n=== ANALIZA CZESTOSCI SLOW (SYSTEM ROZPROSZONY) ===")
    print(f"Przetworzono plikow: {len(files)}")
    top_10 = final_counter.most_common(10)
    for i, (word, count) in enumerate(top_10, 1):
        print(f"{i}. {word}: {count} wystapien")

    print("\n=== POMIARY WYDAJNOSCI ===")
    print(f"Czas calkowity: {execution_time:.2f}s")
    print(f"Czas fazy Map: {map_time:.2f}s")
    print(f"Czas fazy Reduce: {reduce_time:.4f}s")
    
    # Zwracamy krotke z trzema wartosciami - benchmark
    return execution_time, map_time, reduce_time

if __name__ == '__main__':
    mp.freeze_support()
    TARGET_DIR = r".\data\dataset_large"
    WORKER_COUNT = 4
    run_parallel_system(TARGET_DIR, WORKER_COUNT)