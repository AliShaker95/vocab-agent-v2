from app.agent import run_agent

conversations = {}


def handle_message(learner_id: str, text: str) -> dict:
    """Add the learner's message to their conversation, run the agent on it, and return the reply and steps."""
    if learner_id not in conversations:
        conversations[learner_id] = []

    history = conversations[learner_id]

    history.append({"role": "user", "content": text})

    results = run_agent(history)

    return results
