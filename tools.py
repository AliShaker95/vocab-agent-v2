import json
import random

from api_client import call_model

with open("vocab_list.json", encoding="utf-8") as file:
    VOCAB_LIST = json.load(file)

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


def get_vocab(level: str) -> str:
    """Return a random vocabulary item for the selected level."""
    level = level.lower()
    if level in VOCAB_LIST:
        words = VOCAB_LIST.get(level)
        return random.choice(words)
    else:
        return f"Level is invalid! Please select from: {', '.join(VOCAB_LIST)}."


def check_sentence(word: str, sentence: str) -> str:
    """Call the model to check the use of the target word in the sentence without using tools and return the feedback as string."""
    messages = [
        {
            "role": "user",
            "content": f"Check if the target word: '{word}' is correctly used in the sentence: '{sentence}'.",
        }
    ]
    system = "Check whether the learner used the target word in the sentence correctly. Judge only the target word; ignore unrelated mistakes. Give brief feedback."
    response = call_model(messages, system)
    return response["content"][0]["text"]


def run_tool(name: str, tool_input: dict) -> str:
    """Run the required tool by getting its name and input as a dictionary and return the result as string."""
    if name == "get_vocab":
        return get_vocab(tool_input.get("level"))
    elif name == "check_sentence":
        return check_sentence(tool_input.get("word"), tool_input.get("sentence"))
    else:
        return f"Tool '{name}' is not a valid tool!"
