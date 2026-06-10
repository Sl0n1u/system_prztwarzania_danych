import re

def clean_text(text):
    text = text.lower()
    # Usuwanie interpunkcji
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenizacja i filtrowanie liczb
    return [word for word in text.split() if word.isalpha()]