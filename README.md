# Prompt-Smuggler 🥷

**Prompt-Smuggler** is a prompt compression tool that allows advanced developers to define custom "shorthand grammar" in a `.smugglerrc.yaml` dictionary. By swapping massive, recurring prompts with hyper-condensed micro-symbols, it acts as a semantic-shorthand compiler that significantly cuts token overhead, context saturation, and API latency.

## Features 🚀

- **Core Compiler CLI**: Intercepts your raw prompt and replaces custom macros, generating a lightweight `<grammar>` decoder template appended directly to your prompt payload.
- **Cross-Model Token Tracking**: Uses `tiktoken` (for OpenAI) and Hugging Face `transformers` tokenizers (for models like `llama3` and `mistral`) to calculate exact net token savings.
- **Desktop GUI Client (`gui_client.py`)**: A visual drag-and-drop tool for non-coders or those who want an alternative to the CLI to compress prompts before pasting them into standard LLM web interfaces.
- **Jules Benchmarking & Optimization Loop**: A built-in reinforcement-learning style optimization script that tests various shortcut tokens across an LLM endpoint, checking structural fidelity and Semantic Similarity (`sentence-transformers`), auto-updating your `.smugglerrc.yaml` when it finds better compression rules.

## Installation 🛠️

```bash
# Clone the repository
git clone https://github.com/your-username/prompt-smuggler.git
cd prompt-smuggler

# Install Python requirements
pip install -r requirements.txt
```

## Quick Start (CLI Pipeline)

1. Rename `.env.example` to `.env` and set any relevant API keys.
2. Edit your custom shorthand keys in `.smugglerrc.yaml`.
3. Pipe raw prompts through the CLI:

```bash
cat my_prompt.txt | ./smuggler/cli.py
```

The compiled result will be output to standard out (ready to pipe into LLM execution scripts), while live token metrics will be written to standard error.

## Desktop GUI Client

If you prefer a graphical interface to compile your prompts:
```bash
python gui_client.py
```
This opens a clean, dark-themed Tkinter app where you can load markdown/text files or paste raw strings, press `Compress`, and copy the results directly to your clipboard.

## Optimization Loop 🤖

To auto-discover optimal shorthand macros using Dual-Pass Evaluation (Structure parsing + Cosine Distance embedding similarity):

```bash
cd benchmarks
python optimize.py --provider ollama --model llama3 --optimize
```

This will run mutations on your existing rules, executing them against test cases. If a compressed mutation performs structurally and semantically identically to the uncompressed ground truth while saving more tokens, it automatically upgrades your `.smugglerrc.yaml`.
