import os

import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

url = "https://api.anthropic.com/v1/messages"


def get_vocab(level):
    vocab_payload = {
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": f'Give a random vocabulary item (such as single and compound words, collocations, phrasal verbs, idioms etc.) suitable for a learner with the "{level}" level. Give only one item and nothing more.',
            }
        ],
        "model": "claude-haiku-4-5-20251001",
        "stream": False,
        "system": [
            {
                "text": "You help the learner get an important and necessary voacbulary item for their level. Include no text more than the vocabulary item itself that the learner has asked for. The item must be random each time.",
                "type": "text",
            }
        ],
        "temperature": 0.7,
    }
    vocab_response = requests.post(url, headers=headers, json=vocab_payload)
    vocab_data = vocab_response.json()
    return vocab_data["content"][0]["text"]


def check_sentence(word, sentence):
    check_payload = {
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": f'Check if the word "{word}" is correctly used in the sentence "{sentence}" and explain briefly.',
            }
        ],
        "model": "claude-haiku-4-5-20251001",
        "stream": False,
        "system": [
            {
                "text": "You check if the learner has correctly use the target word in the sentence. Ignore irrelevant mistakes and address the ones related to the target word.",
                "type": "text",
            }
        ],
        "temperature": 0.8,
    }
    check_response = requests.post(url, headers=headers, json=check_payload)
    check_data = check_response.json()
    return check_data["content"][0]["text"]


headers = {
    "content-type": "application/json",
    "anthropic-version": "2023-06-01",
    "x-api-key": api_key,
}

tools = [
    {
        "name": "get_vocab",
        "description": "Get a random vocabulary word for a given difficulty level.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "description": "the level of difficulty: beginner, intermediate, or advanced",
                }
            },
            "required": ["level"],
        },
    },
    {
        "name": "check_sentence",
        "description": "Checks whether the learner used the target vocabulary in a sentence correctly or not.",
        "input_schema": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "the target vocabulary word",
                },
                "sentence": {
                    "type": "string",
                    "description": "the sentence written by the learner",
                },
            },
            "required": ["word", "sentence"],
        },
    },
]

levels = ["beginner", "intermediate", "advanced"]
level = input(f"Choose your level: {', '.join(levels)}:\n").strip().lower()

while level not in levels:
    print(f"{level} is not a valid level. Please choose from {', '.join(levels)}.")
    level = input(f"Choose your level: {', '.join(levels)}:\n").strip().lower()

messages = [
    {
        "role": "user",
        "content": f"Give me a random vocabulary for the level{level}. Use the get_vocab tool. Then, explain it briefly and write an example sentence using the target word.",
    }
]

payload = {
    "max_tokens": 1024,
    "messages": messages,
    "tools": tools,
    "model": "claude-haiku-4-5-20251001",
    "stream": False,
    "system": [
        {
            "text": "You help learners practice vocabulary. Always use the get_vocab tool to pick the relevant word. Do not write anything more than what you are asked for.",
            "type": "text",
        }
    ],
    "temperature": 0.7,
}
response = requests.post(url, headers=headers, json=payload)
data = response.json()

word = None

for block in data["content"]:
    if block["type"] == "tool_use":
        assistant_content = data["content"]
        messages.append({"role": "assistant", "content": assistant_content})
        word = get_vocab(block["input"]["level"])
        tool_results = [
            {"type": "tool_result", "tool_use_id": block["id"], "content": word}
        ]
        messages.append({"role": "user", "content": tool_results})
        payload["messages"] = messages
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        for text_block in data["content"]:
            if text_block["type"] == "text":
                print(text_block["text"])
    elif block["type"] == "text":
        print(block["text"])
if word:
    sentence = input(f'Now, use "{word}" in a sentence:\n')
    messages = [
        {
            "role": "user",
            "content": f'Check if the target word "{word}" is correctly used in the sentence "{sentence}" and explain briefly.',
        }
    ]
    payload = {
        "max_tokens": 1024,
        "messages": messages,
        "tools": tools,
        "model": "claude-haiku-4-5-20251001",
        "stream": False,
        "system": [
            {
                "text": "You help learners practice vocabulary. Always use check_sentence tool. Check if the target word is correctly used in the learner's sentence. Ignore irrelevant errors and focus on the target word.",
                "type": "text",
            }
        ],
        "temperature": 0.8,
    }
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()

    for block in data["content"]:
        if block["type"] == "tool_use":
            assistant_content = [block]
            messages.append({"role": "assistant", "content": assistant_content})
            results = check_sentence(block["input"]["word"], block["input"]["sentence"])
            tool_results = [
                {"type": "tool_result", "tool_use_id": block["id"], "content": results}
            ]
            messages.append({"role": "user", "content": tool_results})
            payload["messages"] = messages
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            print(data["content"][0]["text"])
            break
        elif block["type"] == "text":
            print(block["text"])
