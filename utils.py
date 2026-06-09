import string

def clean_text(text):
    # Zamiana na male litery zgodnie ze specyfikacja
    text = text.lower()
    
    # Usuniecie interpunkcji
    for p in string.punctuation:
        text = text.replace(p, ' ')
        
    # Rozbicie na slowa i filtrowanie - zostawiamy tylko slowa skladajace sie z liter (pomijamy liczby)
    words = [word for word in text.split() if word.isalpha()]
    
    return words