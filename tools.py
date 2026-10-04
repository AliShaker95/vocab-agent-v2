import json
import random

with open("vocab_list.json", encoding="utf-8") as file:
    vocab_list = json.load(file)

# Return a random vocabulary item for the selected level.
def get_vocab(level):
    level = level.lower()
    if level in vocab_list:
        words = vocab_list.get(level)
        return random.choice(words)
    else:
        return f"Level is invalid! Please select from: {', '.join(vocab_list)}."

def check_sentence():
    pass