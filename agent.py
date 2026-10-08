from api_client import APIError, call_model
from tools import TOOLS, run_tool

MAX_STEPS = 10
SYSTEM_PROMPT = """You are a vocabulary tutor for English learners.
- When the learner needs a new word, always use get_vocab. Never invent words yourself.
- Explain the word's meaning through simple English and context. Never translate it into another language.
- Give one example sentence, then ask the learner to write their own sentence with the word.
- When the learner writes a sentence with the target word, always use check_sentence and share the feedback.
- If the learner asks a question (about the word, grammar, or anything related), answer it directly and briefly.
- If the learner asks for another word, give one, and if they haven't finished the current word yet, give it if it's related to the current one.
- If the learner is rude or off-topic, stay calm and guide them back to practice.
- Keep replies short and clear, suitable for the learner's level."""


def run_agent(messages: list):
    """Run the agent loop for one user turn: call the model, run any requested tools, and repeat until the model replies with text or the step limit is reached."""
    for step in range(MAX_STEPS):
        try:
            data = call_model(messages, SYSTEM_PROMPT, TOOLS)
        except APIError as e:
            print(f"An error occurred: {e}\nPlease try again later.")
            break
        messages.append({"role": "assistant", "content": data["content"]})

        if data["stop_reason"] != "tool_use":
            for block in data["content"]:
                if block["type"] == "text":
                    print(block["text"])
            break

        results = []
        for block in data["content"]:
            if block["type"] == "tool_use":
                tool_result = run_tool(block["name"], block["input"])
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": tool_result,
                    }
                )
        messages.append({"role": "user", "content": results})
    else:
        print("Sorry, I couldn't finish that. Please try again or rephrase.")
