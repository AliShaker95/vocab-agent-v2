import sys

from app.cost_tracker import resume_cycle_count
from app.sessions import handle_message
from app.tools import VOCAB_LIST

LEVELS = VOCAB_LIST.keys()


def main():
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

    resume_cycle_count()

    user_input = f"My English level is {level}. Give me a vocabulary item to learn."

    while True:
        result = handle_message("admin", user_input)
        print(result["reply"])

        user_input = input("Type your message here:\n")
        while not user_input.strip():
            user_input = input("Type a valid input!\n")

        if user_input.lower().strip() == "quit":
            break


if __name__ == "__main__":
    main()
