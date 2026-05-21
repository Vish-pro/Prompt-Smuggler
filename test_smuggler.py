# Prompt-Smuggler — Local Test Script
# Run from: Prompt-Smuggler directory
# Command:  python test_smuggler.py
# No API key or Ollama needed.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "prompt-smuggler"))

from smuggler.compiler import compile_prompt
from smuggler.tokenizer import calculate_savings

# ── Grammar: define your symbols ──────────────────────────────────────────────
TEST_GRAMMAR = {
    "µ_j":  "Respond with a strictly valid JSON object, omitting any conversational filler or introductory markdown text.",
    "µ_ts": "Use TypeScript, strict typing, interfaces for all props, and prefer functional components.",
    "µ_sr": "You are a senior software engineer. Think step by step before answering. Be concise.",
    "µ_md": "Format your response in clean Markdown with headers, bullet points, and code blocks where relevant.",
}

config = {"grammar": TEST_GRAMMAR}

# ── Test cases ────────────────────────────────────────────────────────────────
tests = [
    {
        "label": "Test 1 — User types symbol directly",
        "prompt": "µ_sr µ_ts Build me a reusable Button component.",
    },
    {
        "label": "Test 2 — User types full phrase (auto-compression)",
        "prompt": (
            "You are a senior software engineer. Think step by step before answering. Be concise. "
            "Use TypeScript, strict typing, interfaces for all props, and prefer functional components. "
            "Build me a reusable Button component."
        ),
    },
    {
        "label": "Test 3 — JSON output + Markdown format",
        "prompt": "µ_j µ_md List the top 5 programming languages in 2026 with pros and cons.",
    },
    {
        "label": "Test 4 — No symbols (no compression expected)",
        "prompt": "What is the capital of France?",
    },
    {
        "label": "Test 5 — Heavy multi-symbol prompt",
        "prompt": (
            "µ_sr µ_ts µ_j µ_md "
            "Design a REST API for a user authentication system. "
            "Include endpoints, request/response shapes, and error codes."
        ),
    },
]

# ── Run tests ─────────────────────────────────────────────────────────────────
SEP = "-" * 65

for test in tests:
    label  = test["label"]
    prompt = test["prompt"]

    compressed_text, grammar_header = compile_prompt(prompt, config)
    full_compressed = f"{grammar_header}\n{compressed_text}".strip() if grammar_header else compressed_text

    savings = calculate_savings(prompt, compressed_text, grammar_header, model="gpt-4o")

    print(SEP)
    print(f"  {label}")
    print(SEP)
    print(f"  ORIGINAL  ({savings['raw_tokens']} tokens):")
    print(f"    {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print()
    print(f"  COMPRESSED ({savings['total_tokens_sent']} tokens sent to LLM):")
    if grammar_header:
        print(f"    {grammar_header}")
    print(f"    {compressed_text}")
    print()

    saved = savings["saved_tokens"]
    ratio = savings["compression_ratio"]
    bar   = "#" * min(int(ratio * 10), 30)

    if saved > 0:
        print(f"  SAVINGS: {saved} tokens saved  |  {ratio:.2f}x compression  {bar}")
    elif saved == 0:
        print(f"  NO COMPRESSION (no symbols matched)")
    else:
        print(f"  OVERHEAD: {abs(saved)} extra tokens (grammar header cost > savings — normal for short prompts)")

    print()

print(SEP)
print("  Done. All tests complete.")
print(SEP)
