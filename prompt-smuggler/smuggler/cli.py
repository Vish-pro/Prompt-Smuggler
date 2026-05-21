#!/usr/bin/env python3
import sys
import argparse
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from smuggler.compiler import compile_prompt, load_config
from smuggler.tokenizer import calculate_savings
from smuggler.session import grammar_already_sent, mark_grammar_sent, clear_session
from smuggler.audit import audit_grammar, print_audit_report
from smuggler.sender import send, DEFAULT_MODELS
from smuggler.daemon import watch, DEFAULT_HOTKEY


def main():
    parser = argparse.ArgumentParser(description="Prompt-Smuggler: Compress prompts using custom symbols.")
    parser.add_argument("--config",      type=str,  default=".smugglerrc.yaml", help="Path to config file.")
    parser.add_argument("--target",      type=str,  default="gpt-4o",           help="Target model for token counting.")
    parser.add_argument("--dry-run",     action="store_true",                   help="Show savings estimate without outputting prompt.")
    parser.add_argument("--session",     type=str,  default=None,               help="Session ID. Grammar header sent only on first call per session.")
    parser.add_argument("--new-session", action="store_true",                   help="Reset session so grammar header is sent again on next call.")
    parser.add_argument("--audit",       action="store_true",                   help="Scan files for symbol usage and report dead symbols. No prompt needed.")
    parser.add_argument("--audit-dir",   type=str,  default=".",                help="Directory to scan for --audit (default: current dir).")
    parser.add_argument("--send",        action="store_true",                   help="Send the compressed prompt to an LLM and print the response.")
    parser.add_argument("--provider",    type=str,  default=None,               help="LLM provider: anthropic | openai | bedrock | ollama | gemini | groq | mistral | azure | huggingface | deepseek | qwen | kimi | yi. Required with --send.")
    parser.add_argument("--model",       type=str,  default=None,               help="Model override. Defaults: anthropic=claude-sonnet-4-6, openai=gpt-4o, bedrock=claude-3-5-sonnet.")
    parser.add_argument("--copy",        action="store_true",                   help="Copy the compressed prompt to clipboard instead of printing. Works with any AI — no API key needed.")
    parser.add_argument("--watch",       action="store_true",                   help="Run as background daemon. Press hotkey to compress clipboard. Works with any AI — no API key needed.")
    parser.add_argument("--hotkey",      type=str,  default=DEFAULT_HOTKEY,     help=f"Hotkey for --watch mode (default: {DEFAULT_HOTKEY}).")
    args = parser.parse_args()

    config  = load_config(args.config)
    grammar = config.get("grammar", {})

    # ── --watch: run daemon, listen for hotkey, compress clipboard ────────────
    if args.watch:
        watch(config_path=args.config, hotkey=args.hotkey)
        sys.exit(0)

    # ── --audit: scan files, report dead symbols, then exit ───────────────────
    if args.audit:
        report = audit_grammar(grammar, scan_dir=args.audit_dir)
        print_audit_report(report)
        sys.exit(0)

    # ── --new-session: wipe session state so grammar is re-sent ───────────────
    if args.new_session and args.session:
        clear_session(args.session)
        print(f"[Prompt-Smuggler] Session '{args.session}' reset. Grammar will be re-sent on next call.", file=sys.stderr)
        sys.exit(0)

    # ── Read prompt from stdin ─────────────────────────────────────────────────
    if sys.stdin.isatty():
        print("Error: No input provided. Use: echo 'your prompt' | smuggler", file=sys.stderr)
        sys.exit(1)

    raw_text = sys.stdin.read()

    # ── Compile ────────────────────────────────────────────────────────────────
    compressed_text, grammar_header = compile_prompt(raw_text, config)

    # ── Problem 2 fix: session-aware grammar header ────────────────────────────
    # If a session is active and the grammar was already sent, strip the header.
    # The LLM already has it in its context — no need to pay for it again.
    if args.session and grammar_header:
        if grammar_already_sent(args.session, grammar):
            grammar_header = ""  # skip header, LLM already knows the grammar
        else:
            mark_grammar_sent(args.session, grammar)  # first call — send and record

    # ── Metrics ────────────────────────────────────────────────────────────────
    savings = calculate_savings(raw_text, compressed_text, grammar_header, args.target)
    saved   = savings["saved_tokens"]
    raw_tok = savings["raw_tokens"]
    pct     = (saved / raw_tok * 100) if raw_tok > 0 else 0

    print(f"\n[Prompt-Smuggler | Target: {args.target}]", file=sys.stderr)
    print(f"  Raw tokens       : {raw_tok}", file=sys.stderr)
    print(f"  Grammar tokens   : {savings['grammar_tokens']}", file=sys.stderr)
    print(f"  Compressed tokens: {savings['compressed_tokens']}", file=sys.stderr)
    print(f"  Total sent       : {savings['total_tokens_sent']}", file=sys.stderr)

    if saved > 0:
        print(f"  Saved            : {saved} tokens ({pct:.1f}% smaller) at {savings['compression_ratio']:.2f}x", file=sys.stderr)
        if args.session:
            print(f"  Session          : '{args.session}' — grammar header {'sent (first call)' if savings['grammar_tokens'] > 0 else 'SKIPPED (already sent)'}", file=sys.stderr)
    elif grammar_header == "" and args.session and savings["compressed_tokens"] < raw_tok:
        print(f"  Session          : '{args.session}' — grammar skipped, saved {raw_tok - savings['compressed_tokens']} tokens this call", file=sys.stderr)
    elif not grammar_header:
        print(f"  Result           : SKIPPED — compression would increase tokens. Sending raw prompt.", file=sys.stderr)
    else:
        print(f"  Result           : No matching symbols found.", file=sys.stderr)

    print("", file=sys.stderr)

    if args.dry_run:
        print("[dry-run] No prompt output. Remove --dry-run to send.", file=sys.stderr)
        sys.exit(0)

    final_prompt = f"{grammar_header}\n\n{compressed_text}" if grammar_header else compressed_text

    # ── --send: deliver compressed prompt to an LLM and print the reply ───────
    if args.copy:
        try:
            import pyperclip
            pyperclip.copy(final_prompt)
            char_count = len(final_prompt)
            tok_count  = savings["total_tokens_sent"]
            raw_tok    = savings["raw_tokens"]
            print(f"[Prompt-Smuggler] Copied to clipboard.", file=sys.stderr)
            print(f"  {char_count} characters | {tok_count} tokens", file=sys.stderr)
            if saved > 0:
                print(f"  Saved {saved} tokens ({pct:.1f}% smaller) vs original", file=sys.stderr)
            print(f"  Paste into claude.ai, ChatGPT, Gemini, or any AI.", file=sys.stderr)
        except ImportError:
            print("Error: Run 'pip install pyperclip' to use --copy", file=sys.stderr)
            sys.exit(1)

    elif args.send:
        if not args.provider:
            print("Error: --send requires --provider (anthropic | openai | bedrock | ollama | gemini | groq | mistral | azure | huggingface | deepseek | qwen | kimi | yi)", file=sys.stderr)
            sys.exit(1)

        default_model = DEFAULT_MODELS.get(args.provider.lower(), "unknown")
        chosen_model  = args.model or default_model
        print(f"[Prompt-Smuggler] Sending to {args.provider} ({chosen_model})...", file=sys.stderr)

        try:
            reply = send(final_prompt, provider=args.provider, model=args.model)
            print(reply)
        except (ImportError, EnvironmentError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        print(final_prompt, end="")


if __name__ == "__main__":
    main()
