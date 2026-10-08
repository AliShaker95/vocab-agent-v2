import os
import sys

import requests
from dotenv import load_dotenv


class APIError(Exception):
    pass


load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    print("The ANTHROPIC_API_KEY is missing. Add it to your .env file.")
    sys.exit()

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

    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        data = response.json()
    except requests.RequestException as e:
        raise APIError(f"Request failed: {e}") from e
    except ValueError as e:
        raise APIError(f"The response from API is not valid JSON: {e}") from e

    if data.get("type") == "error":
        raise APIError(f"API returned an error: {data['error']['message']}")
    return data
