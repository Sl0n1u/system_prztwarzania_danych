import os
import time
import io
import contextlib
import multiprocessing as mp
from sequential import process_directory
from coordinator import run_parallel_system

DATASETS = [
    r".\data\dataset_small",
    r".\data\dataset_medium",
    r".\data\dataset_large"
]
WORKER_COUNTS = [1, 2, 4]
REPETITIONS = 10

def run_benchmark():
    print("=== ROZPOCZYNAM TESTY WYDAJNOSCIOWE ===")
    print(f"Liczba powtorzen dla kazdego pomiaru: {REPETITIONS}\n")
    
    results = {}

    for dataset in DATASETS:
        dataset_name = os.path.basename(dataset)
        if not os.path.exists(dataset):
            print(f"[!] Pomijam {dataset_name} - folder nie istnieje.")
            continue
            
        print(f"-> Testowanie zbioru danych: {dataset_name}")
        results[dataset_name] = {}

        print("   [~] Trwa pomiar wersji sekwencyjnej... ", end="", flush=True)
        seq_times = []
        for i in range(REPETITIONS):
            with contextlib.redirect_stdout(io.StringIO()):
                t = process_directory(dataset)
            seq_times.append(t)
            print(f"[{i+1}: {t:.2f}s] ", end="", flush=True)
            
        avg_seq_time = sum(seq_times) / REPETITIONS
        results[dataset_name]['sequential'] = avg_seq_time
        print(f"Gotowe (Srednia: {avg_seq_time:.2f}s)")

        results[dataset_name]['parallel'] = {}
        for workers in WORKER_COUNTS:
            print(f"   [~] Trwa pomiar dla {workers} workerow... ", end="", flush=True)
            
            # Listy na poszczegolne metryki
            par_times = []
            map_times = []
            reduce_times = []
            
            for i in range(REPETITIONS):
                with contextlib.redirect_stdout(io.StringIO()):
                    # Rozpakowanie 3 wartosci z koordynatora
                    t_total, t_map, t_reduce = run_parallel_system(dataset, num_workers=workers)
                par_times.append(t_total)
                map_times.append(t_map)
                reduce_times.append(t_reduce)
                # Czas calkowity po kazdej iteracji
                print(f"[{i+1}: {t_total:.2f}s] ", end="", flush=True)
                
            avg_par_time = sum(par_times) / REPETITIONS
            avg_map_time = sum(map_times) / REPETITIONS
            avg_reduce_time = sum(reduce_times) / REPETITIONS
            
            speedup = avg_seq_time / avg_par_time
            efficiency = speedup / workers
            
            results[dataset_name]['parallel'][workers] = {
                'time': avg_par_time,
                'map': avg_map_time,
                'reduce': avg_reduce_time,
                'speedup': speedup,
                'efficiency': efficiency
            }
            print(f"Gotowe (Srednia: {avg_par_time:.2f}s)")
        print("-" * 50)

    print("\n\n" + "="*85)
    print(" "*30 + "RAPORT WYDAJNOSCIOWY")
    print("="*85)
    
    for dataset, data in results.items():
        print(f"\nZBIOR DANYCH: {dataset}")
        print(f"Czas sekwencyjny (Baseline): {data['sequential']:.2f}s")
        print("-" * 85)
        print(f"{'Workery':<8} | {'Czas (s)':<9} | {'Map (s)':<9} | {'Reduce (s)':<10} | {'Przyspieszenie':<14} | {'Efektywnosc':<11}")
        print("-" * 85)
        
        for w, m in data['parallel'].items():
            print(f"{w:<8} | {m['time']:<9.2f} | {m['map']:<9.2f} | {m['reduce']:<10.4f} | {m['speedup']:<13.2f}x | {m['efficiency']:<11.2%}")
        print("="*85)

if __name__ == '__main__':
    mp.freeze_support()
    run_benchmark()