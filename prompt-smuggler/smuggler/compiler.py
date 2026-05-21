import yaml
import os
import re

def load_config(config_path: str = ".smugglerrc.yaml") -> dict:
    if not os.path.exists(config_path):
        return {"grammar": {}}

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config or {"grammar": {}}

def generate_grammar_header(grammar: dict) -> str:
    """
    Generates the <grammar> tag containing the decoder dictionary.
    """
    if not grammar:
        return ""

    lines = ["<grammar>"]
    for key, value in grammar.items():
        # Clean newlines from the value if necessary
        cleaned_value = value.replace("\n", " ")
        lines.append(f"{key}:{cleaned_value}")
    lines.append("</grammar>")
    return "\n".join(lines)

def compile_prompt(raw_text: str, config: dict = None) -> tuple[str, str]:
    """
    Scans the raw text and replaces large phrases with their shorthand from the grammar.
    Returns the compressed text and the generated grammar header.
    """
    if config is None:
        config = load_config()

    grammar = config.get("grammar", {})
    if not grammar:
        return raw_text, ""

    compressed_text = raw_text

    # Simple substitution: Replace the exact phrasing with the key.
    # Note: A real implementation might do reverse lookup (find the long string, replace with key)
    # But usually, the user types the key in their prompt, OR the user types the long string.
    # Let's support: user typing the long string -> replace with key for compression.
    # Wait, the prompt says: "replaces massive recurring phrases... with micro-symbols"
    # Actually, in the spec the user typing "Build a React app using µ_boilerplate" means the user types the symbol!
    # Wait, if the user types the symbol, the text ALREADY has the symbol.
    # Let's read Phase 1 again: "replaces matches with the keys, and prepends the dynamically generated mini-dictionary"
    # Oh! Wait, if the user types the raw text, it replaces with keys.
    # Or if the user types the key, it just injects the header.
    # Let's support both: if user types the value, swap it for the key.
    # If the user types the key, keep it and just inject the header.

    used_keys = set()

    # 1. First pass: Replace long values with keys if they exist in the raw text
    for key, value in grammar.items():
        if value in compressed_text:
            compressed_text = compressed_text.replace(value, key)
            used_keys.add(key)

    # 2. Second pass: Check if the user already typed the keys manually
    for key in grammar.keys():
        if key in compressed_text:
            used_keys.add(key)

    # Filter grammar to only include the keys actually used in the prompt
    active_grammar = {k: grammar[k] for k in used_keys}

    grammar_header = generate_grammar_header(active_grammar) if active_grammar else ""

    return compressed_text, grammar_header
