import yaml
import os
import re
from difflib import SequenceMatcher

FUZZY_THRESHOLD = 0.82  # 82% similarity required to auto-compress a sentence


def load_config(config_path: str = ".smugglerrc.yaml") -> dict:
    if not os.path.exists(config_path):
        return {"grammar": {}}
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config or {"grammar": {}}


def generate_grammar_header(grammar: dict) -> str:
    if not grammar:
        return ""
    lines = ["<grammar>"]
    for key, value in grammar.items():
        lines.append(f"{key}:{value.replace(chr(10), ' ')}")
    lines.append("</grammar>")
    return "\n".join(lines)


def _similarity(a: str, b: str) -> float:
    """Similarity ratio between two strings, 0.0 to 1.0."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _split_sentences(text: str) -> list:
    """Split text into sentence chunks for fuzzy matching."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def compile_prompt(raw_text: str, config: dict = None) -> tuple[str, str]:
    """
    Compresses a prompt by replacing grammar matches with their symbols.

    Three passes:
      1. Exact match  — phrase is identical to a grammar value
      2. Symbol match — user already typed the symbol manually
      3. Fuzzy match  — phrase is similar enough (>82%) to a grammar value

    Works identically whether called from CLI, daemon, or desktop app.
    Returns (compressed_text, grammar_header).
    """
    if config is None:
        config = load_config()

    grammar = config.get("grammar", {})
    if not grammar:
        return raw_text, ""

    compressed_text = raw_text
    used_keys = set()

    # ── Pass 1: Exact match ───────────────────────────────────────────────────
    for key, value in grammar.items():
        if value in compressed_text:
            compressed_text = compressed_text.replace(value, key)
            used_keys.add(key)

    # ── Pass 2: Symbol already typed by user ─────────────────────────────────
    for key in grammar:
        if key in compressed_text:
            used_keys.add(key)

    # ── Pass 3: Fuzzy match ───────────────────────────────────────────────────
    # Split into sentences. For each sentence not already compressed,
    # check if it's similar enough to any grammar value.
    sentences = _split_sentences(compressed_text)
    for sentence in sentences:
        if len(sentence) < 25:          # too short to be a meaningful match
            continue
        if any(k in sentence for k in grammar):  # already has a symbol
            continue

        best_key   = None
        best_score = 0.0

        for key, value in grammar.items():
            score = _similarity(sentence, value)
            if score > best_score:
                best_score = score
                best_key   = key

        if best_score >= FUZZY_THRESHOLD and best_key:
            compressed_text = compressed_text.replace(sentence, best_key)
            used_keys.add(best_key)

    # ── Build grammar header with only used symbols ───────────────────────────
    active_grammar = {k: grammar[k] for k in used_keys}
    grammar_header = generate_grammar_header(active_grammar) if active_grammar else ""

    # ── Break-even guard ──────────────────────────────────────────────────────
    from smuggler.tokenizer import count_tokens
    if count_tokens(compressed_text) + count_tokens(grammar_header) >= count_tokens(raw_text):
        return raw_text, ""

    return compressed_text, grammar_header
