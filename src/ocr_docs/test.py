import re

text = "The quick brown fox jumps over the lazy dog"

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

clean_text(text)

print(clean_text(text))