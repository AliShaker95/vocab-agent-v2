import json
import sys
from datetime import datetime

from api_client import MODEL, APIError
from tools import judge_sentence

evals_results = []

try:
    with open("evals_results.json", encoding="utf-8") as file:
        evals_results = json.load(file)
except FileNotFoundError:
    pass
except json.JSONDecodeError as e:
    print(f'Warning: "evals_results.json" is broken, progress may be lost: {e}')
except OSError as e:
    print(f'Warning: could not read "evals_results.json": {e}')

try:
    with open("judge_cases.json", encoding="utf-8") as file:
        test_data = json.load(file)
except FileNotFoundError:
    print('"judge_cases.json" not found!')
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f'The file "judge_cases.json" is not valid JSON: {e}')
    sys.exit(1)
except OSError as e:
    print(f'Could not read "judge_cases.json": {e}')
    sys.exit(1)


def run_eval(test_data: list) -> list:
    results = []
    for item in test_data:
        try:
            correct = judge_sentence(item.get("word"), item.get("sentence")).get(
                "correct"
            )
        except (APIError, json.JSONDecodeError):
            correct = "error"
        results.append(
            {
                "word": item.get("word"),
                "sentence": item.get("sentence"),
                "correct": correct,
                "expected": item.get("expected"),
            }
        )
    return results

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
note = ""

while not note:
    note = input("Enter note: ").strip()
    if not note:
        print("Note cannot be empty.")

evals_results.append(
    {
        "timestamp": timestamp,
        "model": MODEL,
        "note": note,
        "results": run_eval(test_data)
    }
)

with open("evals_results.json", "w", encoding="utf-8") as file:
    json.dump(evals_results, file, indent=2)
