import sys

from agent import run_agent
from tools import VOCAB_LIST

LEVELS = VOCAB_LIST.keys()

while True:
    level = (
        input(
            f'Enter your English level from: {", ".join(LEVELS)}\nType "quit" anytime to quit.\n'
        )
        .strip()
        .lower()
    )

    if level == "quit":
        sys.exit()

    if level in LEVELS:
        break

    print("Not a valid level!")

messages = [
    {
        "role": "user",
        "content": f"My English level is {level}. Give me a vocabulary item to learn.",
    }
]

while True:
    run_agent(messages)

    user_input = input("Type your message here:\n")
    while not user_input.strip():
        user_input = input("Type a valid input!\n")

    if user_input.lower().strip() == "quit":
        break

    messages.append({"role": "user", "content": user_input})
