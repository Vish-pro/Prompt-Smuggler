#!/usr/bin/env python3
import sys
import argparse
import os

# Ensure the parent directory is in the sys.path so we can import from smuggler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smuggler.compiler import compile_prompt, load_config
from smuggler.tokenizer import calculate_savings

def main():
    parser = argparse.ArgumentParser(description="Prompt-Smuggler: Compress prompts using custom symbols.")
    parser.add_argument("--config", type=str, default=".smugglerrc.yaml", help="Path to the config file.")
    parser.add_argument("--target", type=str, default="gpt-4o", help="Target model to calculate token sizes.")
    args = parser.parse_args()

    # Read from standard input (pipe)
    if sys.stdin.isatty():
        print("Error: No input provided. Use it via pipe: cat prompt.txt | smuggler", file=sys.stderr)
        sys.exit(1)

    raw_text = sys.stdin.read()

    config = load_config(args.config)
    compressed_text, grammar_header = compile_prompt(raw_text, config)

    # Calculate savings
    savings = calculate_savings(raw_text, compressed_text, grammar_header, args.target)

    # Print metrics to stderr so it doesn't interrupt the stdout pipe
    print(f"\n[Prompt-Smuggler Metrics | Target: {args.target}]", file=sys.stderr)
    print(f"Raw Tokens:        {savings['raw_tokens']}", file=sys.stderr)
    print(f"Total Sent Tokens: {savings['total_tokens_sent']} (Compressed: {savings['compressed_tokens']}, Grammar: {savings['grammar_tokens']})", file=sys.stderr)
    print(f"Tokens Saved:      {savings['saved_tokens']}", file=sys.stderr)
    print(f"Compression Ratio: {savings['compression_ratio']:.2f}x\n", file=sys.stderr)

    # Output the final prompt to stdout
    final_prompt = f"{grammar_header}\n\n{compressed_text}" if grammar_header else compressed_text
    print(final_prompt, end="")

if __name__ == "__main__":
    main()
