# Tests Problem 2 (session) and Problem 4 (audit)
# Command: python test_session_and_audit.py

import sys, os, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "prompt-smuggler"))

from smuggler.compiler import compile_prompt
from smuggler.tokenizer import calculate_savings
from smuggler.session import grammar_already_sent, mark_grammar_sent, clear_session
from smuggler.audit import audit_grammar, print_audit_report

SEP = "-" * 65

GRAMMAR = {
    "SYS": (
        "You are an expert full-stack software engineer with 15 years of experience "
        "in building production-grade web applications. You follow SOLID principles, "
        "write clean maintainable code, and always consider security, scalability, "
        "and performance. Never truncate code. Write the full implementation."
    ),
    "SEC": (
        "Apply these security rules: validate all user inputs, never expose passwords "
        "or tokens in responses, use parameterized queries, apply rate limiting, "
        "store JWTs in httpOnly cookies, hash passwords with bcrypt 12 rounds, "
        "always verify the requesting user owns the resource before returning data."
    ),
    "DEAD_SYMBOL": (
        "This symbol is defined but nobody uses it. It is just dead weight in the grammar file."
    ),
}

config = {"grammar": GRAMMAR}

# ── PROBLEM 2: SESSION TEST ───────────────────────────────────────────────────
print(SEP)
print("  PROBLEM 2 FIX -- SESSION-AWARE GRAMMAR")
print(SEP)

SESSION_ID = "test_session_123"
clear_session(SESSION_ID)  # start fresh

# Repeat the full instructions 3 times (same pattern as real multi-task prompts)
# so the grammar compression actually wins over the header cost
BLOCK = (
    "You are an expert full-stack software engineer with 15 years of experience "
    "in building production-grade web applications. You follow SOLID principles, "
    "write clean maintainable code, and always consider security, scalability, "
    "and performance. Never truncate code. Write the full implementation. "
    "Apply these security rules: validate all user inputs, never expose passwords "
    "or tokens in responses, use parameterized queries, apply rate limiting, "
    "store JWTs in httpOnly cookies, hash passwords with bcrypt 12 rounds, "
    "always verify the requesting user owns the resource before returning data. "
)

PROMPT = (
    BLOCK + "Task 1: Build a user signup API. "
    + BLOCK + "Task 2: Build a login API that returns a JWT. "
    + BLOCK + "Task 3: Build a protected dashboard route. "
)

for call_number in range(1, 4):
    compressed_text, grammar_header = compile_prompt(PROMPT, config)

    # Session logic: skip header if already sent this session
    header_skipped = False
    if grammar_header:
        if grammar_already_sent(SESSION_ID, GRAMMAR):
            header_skipped = True
            grammar_header = ""
        else:
            mark_grammar_sent(SESSION_ID, GRAMMAR)

    savings = calculate_savings(PROMPT, compressed_text, grammar_header, "gpt-4o")
    sent    = savings["total_tokens_sent"]
    raw     = savings["raw_tokens"]
    saved   = savings["saved_tokens"]
    pct     = (saved / raw * 100) if raw > 0 else 0

    print(f"\n  Call {call_number}:")
    g_tok = savings['grammar_tokens']
    grammar_status = "SKIPPED (LLM already has it)" if header_skipped else f"{g_tok} tokens (sent for first time)"
    print(f"    Grammar header : {grammar_status}")
    print(f"    Raw tokens     : {raw}")
    print(f"    Total sent     : {sent}")
    if saved > 0:
        print(f"    Saved          : {saved} tokens ({pct:.1f}% smaller)")
    else:
        print(f"    Result         : No savings (break-even guard active)")

print()
print("  WHAT THIS MEANS:")
print("  Call 1 pays the grammar cost once. Calls 2 and 3 skip it entirely.")
print("  At 1000 calls, you pay grammar tokens only ONCE instead of 1000 times.")

# ── PROBLEM 4: AUDIT TEST ─────────────────────────────────────────────────────
print()
print(SEP)
print("  PROBLEM 4 FIX -- DEAD SYMBOL AUDIT")
print(SEP)
print()

# Simulate a directory with some prompt files that use SYS and SEC but not DEAD_SYMBOL
with tempfile.TemporaryDirectory() as tmpdir:
    with open(os.path.join(tmpdir, "prompt1.txt"), "w") as f:
        f.write("SYS SEC Build me a login API.")
    with open(os.path.join(tmpdir, "prompt2.txt"), "w") as f:
        f.write("SYS Build me a signup page.")
    # DEAD_SYMBOL intentionally not used in any file

    report = audit_grammar(GRAMMAR, scan_dir=tmpdir)
    print_audit_report(report)

print("  WHAT THIS MEANS:")
print("  DEAD_SYMBOL is defined in your grammar but never appears in any prompt file.")
print("  Every call that includes it wastes those tokens. Remove it.")
print()
print(SEP)
