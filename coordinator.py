import os
import time
import multiprocessing as mp
from collections import Counter
from worker import worker_main

def run_parallel_system(directory_path, num_workers):
    if not os.path.exists(directory_path):
        return 0, 0, 0, []

    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.txt')]
    if not files:
        return 0, 0, 0, []

    task_queue = mp.Queue()
    result_queue = mp.Queue()

    start_time = time.time()

    processes = []
    for i in range(num_workers):
        p = mp.Process(target=worker_main, args=(i, task_queue, result_queue))
        processes.append(p)
        p.start()

    # MAP
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

    # REDUCE
    reduce_start = time.time()
    final_counter = Counter()
    for result in results_list:
        final_counter.update(result["counter"])
        
    reduce_end = time.time()
    reduce_time = reduce_end - reduce_start

    for p in processes:
        p.join()

    end_time = time.time()
    execution_time = end_time - start_time
    
    # Zwracamy czasy oraz gotowa liste Top 10
    top_10 = final_counter.most_common(10)
    
    return execution_time, map_time, reduce_time, top_10

if __name__ == '__main__':
    mp.freeze_support()
    TARGET_DIR = r".\data\dataset_small"
    t_tot, t_map, t_red, top_data = run_parallel_system(TARGET_DIR, 2)
    print(f"Czas: {t_tot:.2f}s, Top 10: {top_data}")