import os
import time
import socket
import json
import threading
import multiprocessing as mp
from collections import Counter
import worker

# Implementacja synchronizacji zgodnie z sekcja 8.2 wytycznych
class ResultCollector:
    def __init__(self, expected_workers):
        self.results = {}
        self.expected_workers = expected_workers
        self.lock = threading.Lock()
        self.complete_event = threading.Event()

    def add_result(self, worker_id, result):
        with self.lock:
            self.results[worker_id] = result
            if len(self.results) == self.expected_workers:
                self.complete_event.set()

def handle_client(conn, collector):
    with conn:
        data = b""
        # Odbieranie strumienia danych TCP do momentu zamkniecia gniazda przez workera
        while True:
            packet = conn.recv(65536)
            if not packet:
                break
            data += packet
        if data:
            try:
                payload = json.loads(data.decode('utf-8'))
                worker_id = payload["worker_id"]
                result_dict = payload["result"]
                collector.add_result(worker_id, result_dict)
            except Exception as e:
                print(f"Blad deserializacji danych: {e}")

def tcp_server_backend(collector, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        
        while not collector.complete_event.is_set():
            try:
                server_socket.settimeout(1.0)
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue
            threading.Thread(target=handle_client, args=(conn, collector), daemon=True).start()

def start_workers(num_workers, coordinator_host, coordinator_port, file_chunks, directory_path):
    processes = []
    for worker_id in range(num_workers):
        # Uruchamianie odrebnych procesow zgodnie z sekcja 8.1
        p = mp.Process(
            target=worker.worker_main, 
            args=(worker_id, coordinator_host, coordinator_port, file_chunks[worker_id], directory_path)
        )
        p.start()
        processes.append(p)
    return processes

def split_files(files, num_workers):
    chunks = [[] for _ in range(num_workers)]
    for idx, filename in enumerate(files):
        chunks[idx % num_workers].append(filename)
    return chunks

if __name__ == '__main__':
    # Parametry uruchomieniowe systemu
    HOST = '127.0.0.1'
    PORT = 50005
    NUM_WORKERS = 2
    DATA_FOLDER = 'student_datasets/dataset_large'
    TIME_SEQUENTIAL = 2.44  # Wartosc uzyskana z Twojego pomiaru sekwencyjnego
    
    if not os.path.exists(DATA_FOLDER):
        print(f"Blad: Folder {DATA_FOLDER} nie istnieje!")
        exit(1)
        
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.txt')]
    if not files:
        print("Nie znaleziono plikow .txt.")
        exit(1)
        
    print(f"Koordynator przygotowuje podzial {len(files)} plikow dla {NUM_WORKERS} workerow...")
    file_chunks = split_files(files, NUM_WORKERS)
    
    # Uruchomienie infrastruktury odbioru danych (Serwer TCP)
    collector = ResultCollector(NUM_WORKERS)
    server_thread = threading.Thread(target=tcp_server_backend, args=(collector, HOST, PORT), daemon=True)
    server_thread.start()
    
    # --- START GLOWNYCH POMIAROW WYDAJNOSCI ---
    start_total = time.perf_counter()
    
    # Początek fazy Map (Praca procesow rownoleglych)
    start_map = time.perf_counter()
    workers = start_workers(NUM_WORKERS, HOST, PORT, file_chunks, DATA_FOLDER)
    
    # Oczekiwanie na event oznaczajacy ze serwer TCP zebral komplet danych
    collector.complete_event.wait()
    end_map = time.perf_counter()
    
    # Początek fazy Reduce (Agregacja struktur w jedna calosc przez Koordynatora)
    start_reduce = time.perf_counter()
    final_counts = Counter()
    for worker_id, local_dict in collector.results.items():
        final_counts.update(local_dict)
    end_reduce = time.perf_counter()
    
    end_total = time.perf_counter()
    # --- KONIEC POMIAROW ---
    
    # Sprzatanie po procesach potomnych
    for p in workers:
        p.join()
        
    # Wyliczanie oficjalnych metryk ze specyfikacji zadania
    time_total = end_total - start_total
    time_map = end_map - start_map
    time_reduce = end_reduce - start_reduce
    speedup = TIME_SEQUENTIAL / time_total
    efficiency = speedup / NUM_WORKERS
    
    # Formatowanie wyniku dokladnie pod szablon sekcji 10 dokumentu projektowego
    print("\n=== ANALIZA CZESTOSCI SLOW ===")
    print("Top 10 najczestszych slow:")
    for idx, (word, count) in enumerate(final_counts.most_common(10), 1):
        print(f"{idx}. {word}: {count} wystapien")
        
    print("\n=== POMIARY WYDAJNOSCI ===")
    print(f"Wersja sekwencyjna: {TIME_SEQUENTIAL:.2f}s")
    print(f"2 workery: {time_total:.2f}s (przyspieszenie: {speedup:.2f}x)")
    print(f"Czas fazy Map: {time_map:.2f}s")
    print(f"Czas fazy Reduce: {time_reduce:.2f}s")
    print(f"Efektywnosc: {efficiency:.2f}")