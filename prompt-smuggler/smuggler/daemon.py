import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smuggler.compiler import compile_prompt, load_config
from smuggler.tokenizer import calculate_savings

DEFAULT_HOTKEY = "ctrl+shift+space"


def _notify(title: str, message: str) -> None:
    """Show a desktop notification. Falls back to console print if plyer unavailable."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Prompt-Smuggler",
            timeout=3,
        )
    except Exception:
        print(f"[Prompt-Smuggler] {message}")


def _compress_clipboard(config: dict) -> None:
    """Read clipboard, compress, write back, notify user."""
    try:
        import pyperclip
    except ImportError:
        print("[Prompt-Smuggler] Error: pip install pyperclip")
        return

    raw = pyperclip.paste()

    if not raw or not raw.strip():
        _notify("Prompt-Smuggler", "Clipboard is empty — nothing to compress.")
        return

    compressed_text, grammar_header = compile_prompt(raw, config)
    final = f"{grammar_header}\n\n{compressed_text}".strip() if grammar_header else compressed_text

    savings  = calculate_savings(raw, compressed_text, grammar_header)
    saved    = savings["saved_tokens"]
    raw_tok  = savings["raw_tokens"]
    ratio    = savings["compression_ratio"]
    pct      = (saved / raw_tok * 100) if raw_tok > 0 else 0

    if saved > 0:
        pyperclip.copy(final)
        _notify(
            "Prompt-Smuggler - Compressed",
            f"Saved {saved} tokens ({pct:.0f}% smaller, {ratio:.1f}x)\nPaste with Ctrl+V"
        )
        print(f"[Prompt-Smuggler] Compressed — {saved} tokens saved ({pct:.0f}%). Paste with Ctrl+V")
    else:
        # No savings — leave clipboard untouched
        _notify(
            "Prompt-Smuggler - No change",
            "Prompt already optimal. Clipboard unchanged."
        )
        print("[Prompt-Smuggler] Already optimal — clipboard unchanged.")


def watch(config_path: str = ".smugglerrc.yaml", hotkey: str = DEFAULT_HOTKEY) -> None:
    """
    Run as a background daemon.
    Press the hotkey to compress whatever is in the clipboard.
    Press Ctrl+C in the terminal to stop.
    """
    try:
        import keyboard
    except ImportError:
        print("Error: Run 'pip install keyboard' to use --watch")
        sys.exit(1)

    config = load_config(config_path)

    print("=" * 50)
    print("  Prompt-Smuggler is running")
    print("=" * 50)
    print(f"  Hotkey  : {hotkey.upper()}")
    print(f"  Config  : {config_path}")
    print()
    print("  HOW TO USE:")
    print("  1. Type your prompt anywhere (Claude, ChatGPT, Gemini)")
    print("  2. Select all your text -> Ctrl+C  (copy it)")
    print(f"  3. Press {hotkey.upper()}  (compress)")
    print("  4. Ctrl+V to paste compressed version")
    print("  5. Hit Send")
    print()
    print("  Press Ctrl+C here to stop the daemon.")
    print("=" * 50)

    keyboard.add_hotkey(hotkey, lambda: _compress_clipboard(config))

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n[Prompt-Smuggler] Stopped.")
