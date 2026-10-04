import os

import requests
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

url = "https://api.anthropic.com/v1/messages"

model = "claude-haiku-4-5-20251001"

headers = {
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01",
    "X-Api-Key": api_key,
}


def call_model(messages: list, system: str | list, tools: list | None = None) -> dict:
    """Call the model with the given messages, system, and tools and return the response as a dictionary."""
    payload = {
        "max_tokens": 1024,
        "messages": messages,
        "model": model,
        "stream": False,
        "system": system,
        "temperature": 0.7,
    }
    # Only the agent's calls get tools. Calls made inside a tool don't.
    if tools:
        payload["tools"] = tools
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
