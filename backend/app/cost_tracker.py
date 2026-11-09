import json
from datetime import datetime

from app.paths import OUTPUT_DIR

COST_LOG_FILE = OUTPUT_DIR / "cost_log.jsonl"
current_cycle = 0
has_started_word = False
total_cycle_cost = 0

# Dollars per 1 million tokens
# Haiku 5.5 prices are for prompts up to 100K tokens (above that, 5x higher)
PRICES = {
    "claude-haiku-5-5": {
        "input": 0.10,
        "output": 0.50,
        "cache_write": 0.125,
        "cache_read": 0.01,
    },
    "claude-haiku-4-5": {
        "input": 1.00,
        "output": 5.00,
        "cache_write": 1.25,
        "cache_read": 0.10,
    },
    "claude-sonnet-4-5": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "claude-sonnet-5-5": {
        "input": 2.00,
        "output": 10.00,
        "cache_write": 2.50,
        "cache_read": 0.10,
    },
}


def resume_cycle_count():
    """Set the current cycle to one after the last cycle in the cost log."""
    global current_cycle, has_started_word

    last_cycle = 0

    if not COST_LOG_FILE.exists():
        current_cycle = 1
        return

    with open(COST_LOG_FILE, encoding="utf-8") as f:
        lines = f.readlines()

    if lines:
        try:
            last_cycle = json.loads(lines[-1])["cycle"]
        except json.JSONDecodeError:
            print("[cost] Warning: last log line is broken, starting from cycle 1.")

    current_cycle = last_cycle + 1
    has_started_word = False


def begin_word_cycle():
    """Start a new word cycle; the first word of a session keeps the number set at startup."""
    global current_cycle, has_started_word

    if has_started_word:
        current_cycle += 1

    has_started_word = True


def calculate_cost(model, input_tokens, output_tokens):
    """Return the cost in dollars of one API call."""
    if model not in PRICES:
        print(f"Warning: no price for model '{model}', cost logged as 0.")
        return 0.0

    price = PRICES[model]
    return (
        input_tokens * price["input"] / 1_000_000
        + output_tokens * price["output"] / 1_000_000
    )


def track_call_cost(response):
    """Read model and token usage from an API response, log the call, and return its cost."""
    model = response["model"]
    input_tokens = response["usage"]["input_tokens"]
    output_tokens = response["usage"]["output_tokens"]

    cost = calculate_cost(model, input_tokens, output_tokens)

    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "cycle": current_cycle,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(COST_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
