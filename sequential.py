import os
import time
from collections import Counter
from utils import clean_text

def process_directory(directory_path):
    if not os.path.exists(directory_path):
        return 0, []

    start_time = time.time()
    total_counter = Counter()

    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    words = clean_text(text)
                    total_counter.update(words)
            except Exception as e:
                pass # Puste, by nie zasmiecac konsoli w benchmarku

    end_time = time.time()
    execution_time = end_time - start_time
    
    # Wyciagamy Top 10 i zwracamy z funkcji jako dane
    top_10 = total_counter.most_common(10)
    
    return execution_time, top_10

if __name__ == "__main__":
    TARGET_DIR = r".\data\dataset_small"
    t, top_data = process_directory(TARGET_DIR)
    print(f"Czas: {t:.2f}s, Top 10: {top_data}")