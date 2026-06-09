import re

def clean_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation, keep only word characters and whitespaces
    text = re.sub(r'[^\w\s]', '', text)
    # Split into tokens and filter out any words containing digits or underscores
    return [word for word in text.split() if word.isalpha()]