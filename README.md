# Vocab Agent v2

A terminal-based AI agent that helps English learners practise vocabulary. It gives level-appropriate words, explains them in simple English (no translation), checks the learner's sentences, looks up pronunciation and word forms, and remembers which words the learner has already learned.

Continues from: https://github.com/AliShaker95/ai-eng-discovery

## How it works

This is an **agent**, not a fixed workflow. On every turn, the model (Claude Haiku 4.5 by default) decides what to do: give a new word, answer a question, check a sentence, or look up a word. The code runs whatever tool the model asks for, sends the result back, and repeats until the model replies with text.

All API calls are made with raw HTTP requests (`requests`), with no SDK.

## Tools

| Tool | What it does |
|---|---|
| `get_vocab` | Picks a random word for the learner's level from `vocab_list.json`, skipping words the learner already knows |
| `check_sentence` | Asks the model whether the target word is used correctly; if it is, saves the word to `known_words.json` |
| `lookup_word` | Gets pronunciation (IPA and audio link), word forms, and part of speech from the Merriam-Webster Learner's Dictionary API |

## Project structure

| File | Purpose |
|---|---|
| `main.py` | Entry point: level selection and the user input loop |
| `agent.py` | The agent loop and the system prompt |
| `tools.py` | Tool functions, tool definitions, and `run_tool` |
| `api_client.py` | Sends requests to the Claude API and raises `APIError` on failure |
| `vocab_list.json` | Word list grouped by level: beginner, intermediate, advanced |
| `known_words.json` | The learner's progress, created automatically (not tracked in git) |
| `vocab_workflow.py` | The earlier fixed-workflow version, kept for comparison |
| `.env.example` | Template for the API keys |

## Setup

1. Install Python 3.12 or newer.
2. Install the dependencies:
   ```
   pip install requests python-dotenv
   ```
3. Copy `.env.example` to `.env` and fill in your keys:
   ```
   ANTHROPIC_API_KEY=your-anthropic-key-here
   MERRIAM_WEBSTER_API_KEY=your-merriam-webster-key-here
   ```
   - Anthropic key: https://console.anthropic.com
   - Merriam-Webster key: https://dictionaryapi.com (register for the **Learner's Dictionary**; keys are per dictionary)

## Run

```
python main.py
```

Choose a level, then chat with the agent. Type `quit` anytime to exit.

To use a different model, change `MODEL` in `api_client.py`.

## Design decisions

- **Deterministic things live in code; uncertain things go to the model.** Level validation and filtering out known words happen in code. Judging whether a sentence is correct is left to the model.
- **Known words are filtered before a word is picked**, so the agent never loops searching for an unused word. When a level is finished, the agent is told so.
- **A word counts as known only after a correct sentence**, not when it is first shown.
- **The dictionary is an enrichment tool, not a word source.** Words come from `vocab_list.json`; the dictionary only adds pronunciation and forms that the model can't reliably produce on its own.
- **Tool calls made inside a tool never get tools**, so the model can't trigger a tool from inside another tool.

## Error handling

- Missing or broken `vocab_list.json`: the program stops with a clear message.
- Broken `known_words.json`: a warning is shown and the program continues.
- Claude API errors (timeout, no connection, invalid response, API error): the turn ends with a message, and the program keeps running.
- Dictionary API errors (unreachable, invalid response, word not found, missing fields): the tool returns a message to the model, which explains it to the learner.
- The agent loop stops after 10 steps per turn to prevent infinite loops.

## Known limitations

- With Claude Haiku 4.5, the model sometimes judges a sentence itself instead of calling `check_sentence`, especially when the learner uses a different form of the word (e.g. "jobs" for "job"). In testing, Claude Sonnet handled this correctly and recognised the different form.
- The audio link is printed as text; the terminal can't play it yet.
