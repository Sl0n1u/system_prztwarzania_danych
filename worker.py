import os
import sys
import socket
import json
from collections import Counter
import utils

def send_result(host, port, result_payload):
    # Dokladna implementacja Wariantu A ze specyfikacji zadania
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(result_payload).encode('utf-8'))

def worker_main(worker_id, coordinator_host, coordinator_port, assigned_files, directory_path):
    print(f"[Worker {worker_id}] Rozpoczynam przetwarzanie {len(assigned_files)} plikow...")
    local_counts = Counter()
    
    # Faza Map: Obliczenia na przydzielonym fragmencie danych
    for filename in assigned_files:
        filepath = os.path.join(directory_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                words = utils.clean_text(text)
                local_counts.update(words)
        except Exception as e:
            print(f"[Worker {worker_id}] Blad podczas czytania pliku {filename}: {e}")
            
    # Przygotowanie struktury sieciowej do wysylki
    payload = {
        "worker_id": worker_id,
        "result": dict(local_counts)
    }
    
    print(f"[Worker {worker_id}] Przetwarzanie zakonczone. Wysylam wyniki do koordynatora przez TCP...")
    try:
        send_result(coordinator_host, coordinator_port, payload)
        print(f"[Worker {worker_id}] Wyniki wyslane pomyslnie.")
    except Exception as e:
        print(f"[Worker {worker_id}] Blad komunikacji TCP: {e}")