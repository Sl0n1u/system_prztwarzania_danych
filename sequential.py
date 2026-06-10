import os
import time
from collections import Counter
from utils import clean_text

def process_directory(directory_path):
    print(f"[Sequential] Starting processing directory: {directory_path}")
    
    if not os.path.exists(directory_path):
        print(f"[Sequential] Error: Directory '{directory_path}' does not exist.")
        return

    # Rozpoczęcie pomiaru czasu
    start_time = time.time()
    
    total_counter = Counter()
    processed_files = 0

    # Iteracja po wszystkich plikach tekstowych w folderze
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    words = clean_text(text)
                    total_counter.update(words)
                    processed_files += 1
            except Exception as e:
                print(f"[Sequential] Error reading {file_path}: {e}")

    # Zakończenie pomiaru czasu
    end_time = time.time()
    execution_time = end_time - start_time

    print("\n=== ANALIZA CZESTOSCI SLOW ===")
    print(f"Przetworzono plikow: {processed_files}")
    print("Top 10 najczestszych slow:")
    
    # Pobranie i sformatowanie 10 najpopularniejszych wyników
    top_10 = total_counter.most_common(10)
    for i, (word, count) in enumerate(top_10, 1):
        print(f"{i}. {word}: {count} wystapien")

    print("\n=== POMIARY WYDAJNOSCI ===")
    print(f"Wersja sekwencyjna: {execution_time:.2f}s")
    return execution_time


if __name__ == "__main__":
    
    TARGET_DIR = r".\data\dataset_large"
    process_directory(TARGET_DIR)