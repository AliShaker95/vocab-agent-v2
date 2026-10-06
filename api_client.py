import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

URL = "https://api.anthropic.com/v1/messages"

MODEL = "claude-haiku-4-5-20251001"

HEADERS = {
    "Content-Type": "application/json",
    "anthropic-version": "2023-06-01",
    "X-Api-Key": API_KEY,
}


def call_model(messages: list, system: str | list, tools: list | None = None) -> dict:
    """Call the model with the given messages, system, and tools and return the response as a dictionary."""
    payload = {
        "max_tokens": 1024,
        "messages": messages,
        "model": MODEL,
        "stream": False,
        "system": system,
        "temperature": 0.7,
    }
    # Only the agent's calls get tools. Calls made inside a tool don't.
    if tools:
        payload["tools"] = tools
    response = requests.post(URL, headers=HEADERS, json=payload)
    return response.json()
