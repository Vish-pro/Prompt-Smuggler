# Prompt-Smuggler

**Bypass LLM token limits and slash your API bills.**  
Pack massive instructions into micro-symbols that any AI natively understands.  
No coding knowledge required.

```
Your 500-token prompt  ──►  [Smuggler]  ──►  µ_j µ_style "Summarise this..."
                                               Saved 70%+ tokens
```

---

## The Problem

Every time you use Claude, ChatGPT, or any AI — you pay for every word you send.

Most people waste thousands of tokens sending the same massive instructions over and over:

> *"Act as an expert software engineer with 15 years of experience... Use TypeScript strict mode... Validate all inputs... Never expose passwords..."*

That's 80 tokens. Every. Single. Request.

**Prompt-Smuggler turns those 80 tokens into 2.**

---

## How It Works

You define a personal shorthand dictionary (takes 2 minutes):

```yaml
# .smugglerrc.yaml
grammar:
  µ_j:     "Respond with a strictly valid JSON object, omitting any conversational filler."
  µ_style: "Use an authoritative corporate tone. Short punchy sentences. Always lead with a summary."
  SYS:     "You are a senior software engineer. Think step by step. Be concise."
```

Then write prompts like this:

```
SYS µ_j Build me a login API with email and password.
```

Prompt-Smuggler detects your symbols, bundles a compact decoder header, and sends the whole thing to the AI in a fraction of the original tokens.

**The AI gets your full instructions. You pay for almost nothing.**

---

## Features

- **70%+ token compression** on repeated instruction blocks
- **Break-even guard** — if compression won't help, it sends the original untouched. You never pay more than without the tool.
- **Works with any AI** — Claude, ChatGPT, Gemini, DeepSeek, Grok, local models, anything
- **No API key needed** to compress — just copy and paste the output anywhere
- **Session-aware** — grammar header sent only once per conversation, not on every message
- **Dead symbol audit** — find unused symbols wasting space in your grammar file
- **Desktop app** — GUI for non-coders, no terminal needed
- **Global hotkey daemon** — compress clipboard with one keypress from any app

---

## Supported AI Providers

| Provider | Command |
|---|---|
| Anthropic (Claude) | `--provider anthropic` |
| OpenAI (GPT) | `--provider openai` |
| AWS Bedrock | `--provider bedrock` |
| Google Gemini | `--provider gemini` |
| Groq | `--provider groq` |
| Mistral | `--provider mistral` |
| Azure OpenAI | `--provider azure` |
| HuggingFace | `--provider huggingface` |
| Ollama (local, free) | `--provider ollama` |
| DeepSeek | `--provider deepseek` |
| Qwen / Alibaba | `--provider qwen` |
| Kimi / Moonshot | `--provider kimi` |
| Yi / 01.AI | `--provider yi` |

---

## Quick Start

### Option A — Desktop App (No coding needed)

```bash
pip install -e ".[watch]"
python desktop/app.py
```

Paste your prompt → Click **Compress** → Click **Copy** → Paste into any AI.

---

### Option B — Global Hotkey (One keypress from anywhere)

```bash
pip install -e ".[watch]"
smuggler --watch
```

Then from any app — Claude Desktop, ChatGPT, Gemini, anything:

1. Type your prompt
2. `Ctrl+A` → `Ctrl+C`
3. Press `Ctrl+Shift+Space`
4. Notification: *"Saved 47 tokens (58%). Paste with Ctrl+V"*
5. `Ctrl+A` → `Ctrl+V` → Send

---

### Option C — CLI (For developers)

```bash
# Install core only
pip install -e "."

# Install with a specific provider
pip install -e ".[anthropic]"
pip install -e ".[deepseek]"
pip install -e ".[all]"         # every provider

# Compress and copy to clipboard
echo "SYS µ_j Build a login API" | smuggler --copy

# Compress and send directly to an AI
echo "SYS µ_j Build a login API" | smuggler --send --provider anthropic

# Preview savings without sending
echo "SYS µ_j Build a login API" | smuggler --dry-run

# Pipe into any AI tool
cat my_prompt.txt | smuggler | llm-cli
```

---

## Setup

### 1. Clone

```bash
git clone https://github.com/Vish-pro/Prompt-Smuggler.git
cd Prompt-Smuggler/prompt-smuggler
```

### 2. Install

```bash
pip install -e "."              # core only
pip install -e ".[anthropic]"   # + Claude
pip install -e ".[openai]"      # + GPT
pip install -e ".[ollama]"      # + local AI (free, no key)
pip install -e ".[all]"         # everything
```

### 3. Add your API key (only needed for --send)

```bash
cp .env.example .env
# Open .env and fill in your key
```

### 4. Define your grammar

```yaml
# .smugglerrc.yaml
grammar:
  SYS:  "You are a senior software engineer. Think step by step. Be concise."
  SEC:  "Validate all inputs. Never expose passwords. Use parameterised queries."
  µ_j:  "Respond with a strictly valid JSON object, no filler or markdown."
```

---

## Token Efficiency

Real test — same instructions sent 3 times (common in multi-task prompts):

| | Tokens |
|---|---|
| Without Prompt-Smuggler | 537 |
| With Prompt-Smuggler | 230 |
| **Saved** | **307 tokens (57%)** |

At scale with GPT-4o pricing ($2.50 / 1M tokens):

| Calls | Tokens saved | Money saved |
|---|---|---|
| 1,000 | 307,000 | $0.77 |
| 10,000 | 3,070,000 | $7.68 |
| 100,000 | 30,700,000 | **$76.75** |

---

## All CLI Flags

| Flag | What it does |
|---|---|
| `--copy` | Compress and copy to clipboard. Works with any AI, no key needed. |
| `--send` | Compress and send to an AI, print the response. |
| `--provider` | Which AI to use with `--send`. |
| `--model` | Override the default model for your provider. |
| `--dry-run` | Show token savings without outputting anything. |
| `--watch` | Run as background daemon. Hotkey compresses your clipboard. |
| `--hotkey` | Custom hotkey for `--watch` (default: `ctrl+shift+space`). |
| `--session` | Session ID — grammar sent only on first call, skipped after. |
| `--new-session` | Reset session so grammar is re-sent on next call. |
| `--audit` | Scan your prompt files and report dead unused symbols. |
| `--audit-dir` | Directory to scan for `--audit`. |
| `--config` | Path to a custom `.smugglerrc.yaml` file. |

---

## Project Structure

```
Prompt-Smuggler/
├── desktop/                  ← Desktop GUI app (for non-coders)
│   └── app.py
└── prompt-smuggler/          ← CLI tool and core engine
    ├── pyproject.toml
    ├── .smugglerrc.yaml      ← Your symbol grammar
    ├── .env.example          ← API key template
    └── smuggler/
        ├── compiler.py       ← Core compression engine
        ├── tokenizer.py      ← Token counting (tiktoken)
        ├── sender.py         ← 13 AI provider integrations
        ├── session.py        ← Session-aware grammar caching
        ├── daemon.py         ← Global hotkey background daemon
        ├── audit.py          ← Dead symbol scanner
        └── cli.py            ← Command line interface
```

---

## Pro Tips

**Non-coders using Claude Desktop or ChatGPT:**
Run `smuggler --watch` once when you sit down to work. Press `Ctrl+Shift+Space` to compress anything you copy. Never touch the terminal again.

**Developers on API:**
Use `--session myapp` so the grammar header is sent only on the first call. Every call after skips it entirely — maximum savings at scale.

**Local AI users (Ollama):**
Keeping prompts compressed is the fastest way to stop your CPU fan sounding like a jet engine on long generations.

---

## Why "Already optimal"?

If you see this message, your prompt doesn't contain any symbols or phrases from your `.smugglerrc.yaml`. The tool only compresses what it recognises.

**Fix:** Add a symbol to your grammar, then use it in your prompt:
```yaml
grammar:
  SYS: "You are a helpful assistant."
```
Then type: `SYS What is the capital of France?`

---

## License

MIT — free to use, modify, and distribute.

---

*Built by [Vish-pro](https://github.com/Vish-pro)*
