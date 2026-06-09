import os
import time
import threading
import multiprocessing as mp
from collections import Counter

# Importujemy logike z naszych istniejacych modulow
import utils
from coordinator import ResultCollector, tcp_server_backend, start_workers, split_files

def run_sequential(data_folder, file_list):
    start = time.perf_counter()
    total_counts = Counter()
    for filename in file_list:
        filepath = os.path.join(data_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()
            words = utils.clean_text(text)
            total_counts.update(words)
    return time.perf_counter() - start

def run_distributed(num_workers, data_folder, file_list, port):
    host = '127.0.0.1'
    file_chunks = split_files(file_list, num_workers)
    collector = ResultCollector(num_workers)
    
    # Uruchomienie serwera na dynamicznie przydzielonym porcie
    server_thread = threading.Thread(target=tcp_server_backend, args=(collector, host, port), daemon=True)
    server_thread.start()
    
    # Krotki bufor czasu, aby serwer zdazyl zablindowac port
    time.sleep(0.05) 
    
    start_total = time.perf_counter()
    
    # FAZA MAP
    start_map = time.perf_counter()
    workers = start_workers(num_workers, host, port, file_chunks, data_folder)
    collector.complete_event.wait()
    end_map = time.perf_counter()
    
    # FAZA REDUCE
    start_reduce = time.perf_counter()
    final_counts = Counter()
    for worker_id, local_dict in collector.results.items():
        final_counts.update(local_dict)
    end_reduce = time.perf_counter()
    
    end_total = time.perf_counter()
    
    # Zamkniecie procesow podrzędnych
    for p in workers:
        p.join()
        
    time_map = end_map - start_map
    time_reduce = end_reduce - start_reduce
    time_tot = end_total - start_total
    
    return time_tot, time_map, time_reduce

if __name__ == '__main__':
    REPETITIONS = 3
    WORKER_COUNTS = [1, 2, 4]
    DATA_FOLDER = 'student_datasets/dataset_large'
    
    all_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.txt')]
    all_files.sort() # Zapewnienie powtarzalnosci zestawow
    
    # Definiowanie zestawow zgodnie z wymogami projektu
    SCENARIOS = {
        "Maly (3 pliki)": all_files[:3],
        "Sredni (6 plikow)": all_files[:6],
        "Duzy (10 plikow)": all_files[:10]
    }
    
    print(f"\n{'ZBIOR':<18} | {'WORKERY':<8} | {'CZAS CALKOWITY':<15} | {'MAP':<10} | {'REDUCE':<10} | {'PRZYSPIESZENIE':<15} | {'EFEKTYWNOSC':<12}")
    print("-" * 105)
    
    # Zaczynamy od bezpiecznego portu
    base_port = 50100
    port_offset = 0
    
    for scenario_name, file_list in SCENARIOS.items():
        # Baza sekwencyjna (srednia z 3 uruchomien)
        seq_times = []
        for _ in range(REPETITIONS):
            seq_times.append(run_sequential(DATA_FOLDER, file_list))
        avg_seq_time = sum(seq_times) / REPETITIONS
        
        print(f"{scenario_name:<18} | {'Sekwenc.':<8} | {avg_seq_time:>12.3f} s | {'-':<10} | {'-':<10} | {'1.00x':>14} | {'-':<12}")
        
        # Testy rozproszone
        for w in WORKER_COUNTS:
            dist_times, map_times, red_times = [], [], []
            
            for r in range(REPETITIONS):
                current_port = base_port + port_offset
                port_offset += 1
                
                t_tot, t_map, t_red = run_distributed(w, DATA_FOLDER, file_list, current_port)
                dist_times.append(t_tot)
                map_times.append(t_map)
                red_times.append(t_red)
                
                # Zabezpieczenie przed przepelnieniem zasobow sieciowych miedzy iteracjami
                time.sleep(0.1) 
                
            avg_tot = sum(dist_times) / REPETITIONS
            avg_map = sum(map_times) / REPETITIONS
            avg_red = sum(red_times) / REPETITIONS
            
            speedup = avg_seq_time / avg_tot
            efficiency = speedup / w
            
            print(f"{'':<18} | {w:<8} | {avg_tot:>12.3f} s | {avg_map:>8.3f} s | {avg_red:>8.3f} s | {speedup:>13.2f}x | {efficiency:>12.2f}")
            
        print("-" * 105)