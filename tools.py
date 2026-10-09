import json
import random
import sys

from api_client import APIError, call_model

try:
    with open("vocab_list.json", encoding="utf-8") as file:
        VOCAB_LIST = json.load(file)
except FileNotFoundError:
    print('"vocab_list.json" not found!')
    sys.exit()
except json.JSONDecodeError as e:
    print(f'The file "vocab_list.json" is not valid JSON: {e}')
    sys.exit()
except OSError as e:
    print(f'Could not read "vocab_list.json": {e}')
    sys.exit()

known_words = {level: [] for level in VOCAB_LIST}

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
    """Call the model to check the use of the target word in the sentence without using tools and return the feedback as string."""
    messages = [
        {
            "role": "user",
            "content": f"Check if the target word: '{word}' is correctly used in the sentence: '{sentence}'.",
        }
    ]
    system = """Check whether the learner used the target word in the sentence correctly. Judge only the target word; ignore unrelated mistakes. Give brief feedback.
    Reply with only JSON, no other text, in this exact format:
    {"correct": true or false, "feedback": "brief feedback for the learner"}"""

    try:
        response = call_model(messages, system)
    except APIError as e:
        return f"Couldn't check the sentence: {e}"

    text = (
        response["content"][0]["text"]
        .strip()
        .removeprefix("```json")
        .removesuffix("```")
        .strip()
    )
    try:
        verdict = json.loads(text)
    except json.JSONDecodeError:
        return text

    if verdict.get("correct"):
        update_known_words(word)

    return verdict.get("feedback", text)


def run_tool(name: str, tool_input: dict) -> str:
    """Run the required tool by getting its name and input as a dictionary and return the result as string."""
    if name == "get_vocab":
        return get_vocab(tool_input.get("level"))
    elif name == "check_sentence":
        return check_sentence(tool_input.get("word"), tool_input.get("sentence"))
    else:
        return f"Tool '{name}' is not a valid tool!"
