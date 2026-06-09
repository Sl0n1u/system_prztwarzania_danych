import os
import time
from collections import Counter
import utils

def process_files_sequential(directory_path):
    total_counts = Counter()
    
    # Pobranie listy plikow .txt z podanego folderu
    if not os.path.exists(directory_path):
        print(f"Blad: Folder {directory_path} nie istnieje!")
        return total_counts
        
    files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
    
    if not files:
        print("Nie znaleziono plikow .txt w folderze.")
        return total_counts

    print(f"Znaleziono {len(files)} plikow. Rozpoczynam przetwarzanie sekwencyjne...")
    
    # Przetwarzanie kazdego pliku jeden po drugim
    for filename in files:
        filepath = os.path.join(directory_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
                words = utils.clean_text(text)
                total_counts.update(words)
        except Exception as e:
            print(f"Blad podczas czytania pliku {filename}: {e}")
            
    return total_counts

if __name__ == '__main__':
    # Zakladamy, ze dane sa w folderze 'student_datasets/dataset_large'
    # (musisz wczesniej uruchomic skrypt do generowania danych)
    data_folder = 'student_datasets/dataset_large'
    
    start_time = time.perf_counter()
    result = process_files_sequential(data_folder)
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time
    
    print("\n=== WYNIKI (Wersja Sekwencyjna) ===")
    print(f"Czas wykonania: {execution_time:.2f} s")
    print("Top 10 najczestszych slow:")
    
    # Wyswietlenie 10 najczestszych slow
    for word, count in result.most_common(10):
        print(f"{word}: {count}")