import json
import os
import random
import sys

import requests

from api_client import APIError, call_model

DICTIONARY_URL = "https://www.dictionaryapi.com/api/v3/references/learners/json/"
DICTIONARY_API_KEY = os.getenv("MERRIAM_WEBSTER_API_KEY")

try:
    with open("vocab_list.json", encoding="utf-8") as file:
        VOCAB_LIST = json.load(file)
except FileNotFoundError:
    print('"vocab_list.json" not found!')
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f'The file "vocab_list.json" is not valid JSON: {e}')
    sys.exit(1)
except OSError as e:
    print(f'Could not read "vocab_list.json": {e}')
    sys.exit(1)

known_words = {}

try:
    with open("known_words.json", encoding="utf-8") as file:
        known_words = json.load(file)
except FileNotFoundError:
    pass
except json.JSONDecodeError as e:
    print(f'Warning: "known_words.json" is broken, progress may be lost: {e}')
except OSError as e:
    print(f'Warning: could not read "known_words.json": {e}')

TOOLS = [
    {
        "name": "get_vocab",
        "description": "Get a new vocabulary item for the learner's level. Use it whenever the learner needs a new word, including when they ask for another one for clarification. Don't invent words yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "description": f"level of the learner: {', '.join(VOCAB_LIST)}",
                }
            },
            "required": ["level"],
        },
    },
    {
        "name": "check_sentence",
        "description": "Check whether the learner used the target word correctly in their sentence. Use it whenever the learner writes a sentence with the target word. Don't use it for questions or other messages.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "The target word",
                },
                "sentence": {
                    "type": "string",
                    "description": "The sentence to be checked with the target word in it.",
                },
            },
            "required": ["word", "sentence"],
        },
    },
    {
        "name": "lookup_word",
        "description": "Look up a word and return its pronunciation (IPA and audio link), word forms, and part of speech. Use it whenever you introduce a new word from get_vocab, and whenever the learner asks about pronunciation, forms, or part of speech of any word.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "The word to be looked up.",
                }
            },
            "required": ["word"],
        },
    },
]


def update_known_words(learned_word: str):
    learned_word = learned_word.strip().lower()
    for level, words in VOCAB_LIST.items():
        known_words.setdefault(level, [])
        if learned_word in words:
            if learned_word in known_words[level]:
                break
            known_words[level].append(learned_word)
            with open("known_words.json", "w", encoding="utf-8") as file:
                json.dump(known_words, file, indent=2)
            break


def get_vocab(level: str) -> str:
    """Return a random vocabulary item for the selected level."""
    if not level:
        return f"No level given. Please call get_vocab with one of: {', '.join(VOCAB_LIST)}"

    level = level.strip().lower()
    if level not in VOCAB_LIST:
        return f"Level is invalid! Please select from: {', '.join(VOCAB_LIST)}."

    words = VOCAB_LIST.get(level)
    known = known_words.get(level, [])
    available = [word for word in words if word not in known]
    if not available:
        return f"The learner has learned every word in the {level} level. Tell them they finished this level and suggest choosing another one."
    word = random.choice(available)
    return word


def check_sentence(word: str, sentence: str) -> str:
    """Judge the learner's sentence, save the word to known words if it is correct, and return the feedback for Claude, or an error message if the check failed."""

    try:
        check_result = judge_sentence(word, sentence)
    except (APIError, json.JSONDecodeError) as e:
        return f"Couldn't check the sentence: {e}"

    if check_result.get("correct"):
        update_known_words(word)

    return check_result.get("feedback", "No feedback given.")


def judge_sentence(word: str, sentence: str) -> dict:
    """Ask the model whether the target word is used correctly in the sentence and return the verdict as a dict with "correct" and "feedback". Raises APIError or json.JSONDecodeError on failure."""

    messages = [
        {
            "role": "user",
            "content": f"Check if the target word: '{word}' is correctly used in the sentence: '{sentence}'.",
        }
    ]
    system = """Check whether the learner used the target word in the sentence correctly. Judge only the target word; ignore unrelated mistakes. Give brief feedback.
    Reply with only JSON, no other text, in this exact format:
    {"correct": true or false, "feedback": "brief feedback for the learner"}"""

    response = call_model(messages, system)
    text = (
        response["content"][0]["text"]
        .strip()
        .removeprefix("```json")
        .removesuffix("```")
        .strip()
    )
    verdict = json.loads(text)

    return verdict


def lookup_word(word: str) -> str:
    if not word:
        return "No word given. Please give a word when call lookup_word."

    word = word.strip().lower()

    try:
        response = requests.get(
            DICTIONARY_URL + word, params={"key": DICTIONARY_API_KEY}, timeout=10
        )
    except requests.RequestException as e:
        return f"Couldn't get the data!: {e}"

    if response.status_code != 200:
        return "Couldn't get the data!"

    try:
        data = response.json()
    except ValueError as e:
        return f"Couldn't read the dictionary response: {e}"

    if not data or not isinstance(data[0], dict):
        return f"No dictionary entry found for '{word}'."

    entry = data[0]

    try:
        pro = entry["hwi"]["prs"][0]
    except (KeyError, IndexError):
        pro = {}

    ipa = pro.get("ipa")
    audio = pro.get("sound", {}).get("audio")

    if audio:
        if audio.startswith("bix"):
            folder = "bix"
        elif audio.startswith("gg"):
            folder = "gg"
        elif not audio[0].isalpha():
            folder = "number"
        else:
            folder = audio[0]

    audio_link = (
        f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{folder}/{audio}.mp3"
        if audio
        else None
    )

    pos = entry.get("fl")

    forms = [
        item["if"].replace("*", "") for item in entry.get("ins", []) if "if" in item
    ]

    return (
        f"Word: {word}\n"
        f"Pronunciation(IPA): {ipa or 'not available.'}\n"
        f"Audio Link: {audio_link or 'not available.'}\n"
        f"Part of Speech: {pos or 'not available.'}\n"
        f"Forms: {', '.join(forms) or 'not available.'}"
    )


def run_tool(name: str, tool_input: dict) -> str:
    """Run the required tool by getting its name and input as a dictionary and return the result as string."""
    if name == "get_vocab":
        return get_vocab(tool_input.get("level"))
    elif name == "check_sentence":
        return check_sentence(tool_input.get("word"), tool_input.get("sentence"))
    elif name == "lookup_word":
        return lookup_word(tool_input.get("word"))
    else:
        return f"Tool '{name}' is not a valid tool!"
