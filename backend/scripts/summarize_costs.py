import json

from app.paths import OUTPUT_DIR, SCRIPTS_DIR

COST_LOG_FILE = OUTPUT_DIR / "cost_log.jsonl"
SUMMARY_FILE = SCRIPTS_DIR / "results" / "cost_summary.json"


def load_calls():
    """Read every API call from the cost log and return them as a list of dicts."""
    calls = []

    with open(COST_LOG_FILE, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                calls.append(json.loads(line))

    return calls


def total_per_cycle(calls: list):
    """Add up calls, tokens and cost for each cycle and return a list of cycle totals"""
    cycles = {}

    for call in calls:
        number = call["cycle"]
        if number not in cycles:
            cycles[number] = {
                "cycle": number,
                "calls": 0,
                "models": [],
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
            }

        cycles[number]["calls"] += 1
        if call["model"] not in cycles[number]["models"]:
            cycles[number]["models"].append(call["model"])
        cycles[number]["input_tokens"] += call["input_tokens"]
        cycles[number]["output_tokens"] += call["output_tokens"]
        cycles[number]["cost"] += call["cost"]

    return list(cycles.values())


def main():
    if not COST_LOG_FILE.exists():
        print("No cost log found. Run the app first.")
        return

    cycles = total_per_cycle(load_calls())
    if not cycles:
        print("The cost log has no cycles yet.")
        return

    total_cost = sum(c["cost"] for c in cycles)
    average_cost = total_cost / len(cycles)
    summary = {
        "cycles_counted": len(cycles),
        "total_cost": total_cost,
        "average_cost_per_cycle": average_cost,
        "cycles": cycles,
    }

    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Cycles: {len(cycles)}")
    print(f"Total cost: ${total_cost:.6f}")
    print(f"Average per cycle: ${average_cost:.6f}")
    print(f"Saved to {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
