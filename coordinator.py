import os
import time
import multiprocessing as mp
from collections import Counter
from worker import worker_main

def run_parallel_system(directory_path, num_workers):
    print(f"[Coordinator] Rozpoczynam przetwarzanie w '{directory_path}' z {num_workers} workerami.")
    
    if not os.path.exists(directory_path):
        print(f"[Coordinator] Blad: Folder '{directory_path}' nie istnieje.")
        return

    # Pobranie listy plikow
    files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.txt')]
    if not files:
        print("[Coordinator] Brak plikow do przetworzenia.")
        return

    # Inicjalizacja kolejek (Wariant C)
    task_queue = mp.Queue()
    result_queue = mp.Queue()

    # Start pomiaru czasu (obejmuje narzut na powolywanie procesow)
    start_time = time.time()

    # Uruchamianie workerow
    processes = []
    for i in range(num_workers):
        p = mp.Process(target=worker_main, args=(i, task_queue, result_queue))
        processes.append(p)
        p.start()

    # Faza Map: Rozsylanie zadan (sciezek do plikow)
    for file_path in files:
        task_queue.put(file_path)

    # Wysylanie syngalu zakonczenia - po jednym dla kazdego workera
    for _ in range(num_workers):
        task_queue.put(None)

    # Faza Reduce: Zbieranie i agregacja wynikow
    final_counter = Counter()
    workers_finished = 0
    
    while workers_finished < num_workers:
        result = result_queue.get()
        worker_id = result["worker_id"]
        worker_counter = result["counter"]
        print(f"[Coordinator] Odebrano wyniki od Workera {worker_id}")
        
        # Szybka agregacja wynikow czastkowych
        final_counter.update(worker_counter)
        workers_finished += 1

    # Czekanie az wszystkie procesy czysto sie zakoncza (dobra praktyka)
    for p in processes:
        p.join()

    # Koniec pomiaru czasu
    end_time = time.time()
    execution_time = end_time - start_time

    # Wyswietlanie wynikow
    print("\n=== ANALIZA CZESTOSCI SLOW (SYSTEM ROZPROSZONY) ===")
    print(f"Przetworzono plikow: {len(files)}")
    print("Top 10 najczestszych slow:")
    
    top_10 = final_counter.most_common(10)
    for i, (word, count) in enumerate(top_10, 1):
        print(f"{i}. {word}: {count} wystapien")

    print("\n=== POMIARY WYDAJNOSCI ===")
    print(f"Czas wykonania ({num_workers} workery): {execution_time:.2f}s")
    
    return execution_time

if __name__ == '__main__':
    # Wymagane dla poprawnego dzialania multiprocessing na systemie Windows
    mp.freeze_support()
    
    # Sciezka testowa
    TARGET_DIR = r".\data\dataset_small"
    
    # Uruchomienie z 2 workerami (minimalna architektura)
    run_parallel_system(TARGET_DIR, num_workers=2)