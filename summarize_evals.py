import json
import sys

try:
    with open("evals_results.json", encoding="utf-8") as file:
        evals_results = json.load(file)
except FileNotFoundError:
    print('File "evals_results.json" not found!')
    sys.exit(1)
except (json.JSONDecodeError, OSError) as e:
    print(f'Could not read "evals_results.json": {e}')
    sys.exit(1)

summary = (
    "# Judge evaluation results\n\n"
    "| Run | Note | Model | Agreed | Errors | Agreement |\n"
    "|---|---|---|---|---|---|\n"
)

for run in evals_results:
    timestamp = run.get("timestamp")
    note = run.get("note")
    model = run.get("model")
    if model and model[-8:].isdigit():
        model = model[:-9]
    total = 0
    agreed = 0
    errors = 0
    for result in run["results"]:
        if result["correct"] == result["expected"]:
            agreed += 1
        elif result["correct"] == "error":
            errors += 1
        total += 1

    checked = total - errors
    
    if checked == 0:
        continue

    summary += f"| {timestamp} | {note} | {model} | {agreed}/{checked} | {errors} | {agreed / checked * 100:.1f}% |\n"

try:
    with open("RESULTS.md", "w", encoding="utf-8") as file:
        file.write(summary)
except OSError as e:
    print(f'Could not write "RESULTS.md": {e}')
    sys.exit(1)
