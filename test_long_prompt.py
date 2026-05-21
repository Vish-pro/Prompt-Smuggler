# Prompt-Smuggler -- Real Savings Test
# Command: python test_long_prompt.py

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "prompt-smuggler"))

from smuggler.compiler import compile_prompt
from smuggler.tokenizer import calculate_savings

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
    "TS": (
        "Use TypeScript strict mode. All functions need explicit return types. "
        "Use interfaces over type aliases. Prefer async/await. Never use 'any'. "
        "All React components must be functional with typed props interfaces. "
        "Use named exports. kebab-case files, camelCase variables, PascalCase classes."
    ),
}

config = {"grammar": GRAMMAR}

print(SEP)
print("  PROMPT-SMUGGLER -- WHERE IT ACTUALLY SAVES TOKENS")
print(SEP)

# -------------------------------------------------------------------
# SCENARIO: A developer building a multi-part system needs to repeat
# the same instructions across multiple tasks in one big prompt.
# This is common in batch prompts or chained instruction sets.
# -------------------------------------------------------------------

RAW = (
    # Task 1 repeats the full system instructions
    "You are an expert full-stack software engineer with 15 years of experience "
    "in building production-grade web applications. You follow SOLID principles, "
    "write clean maintainable code, and always consider security, scalability, "
    "and performance. Never truncate code. Write the full implementation. "
    "Use TypeScript strict mode. All functions need explicit return types. "
    "Use interfaces over type aliases. Prefer async/await. Never use 'any'. "
    "All React components must be functional with typed props interfaces. "
    "Use named exports. kebab-case files, camelCase variables, PascalCase classes. "
    "Apply these security rules: validate all user inputs, never expose passwords "
    "or tokens in responses, use parameterized queries, apply rate limiting, "
    "store JWTs in httpOnly cookies, hash passwords with bcrypt 12 rounds, "
    "always verify the requesting user owns the resource before returning data. "
    "Task 1: Build the user signup API route with email and password. "

    # Task 2 repeats the SAME instructions again
    "You are an expert full-stack software engineer with 15 years of experience "
    "in building production-grade web applications. You follow SOLID principles, "
    "write clean maintainable code, and always consider security, scalability, "
    "and performance. Never truncate code. Write the full implementation. "
    "Use TypeScript strict mode. All functions need explicit return types. "
    "Use interfaces over type aliases. Prefer async/await. Never use 'any'. "
    "All React components must be functional with typed props interfaces. "
    "Use named exports. kebab-case files, camelCase variables, PascalCase classes. "
    "Apply these security rules: validate all user inputs, never expose passwords "
    "or tokens in responses, use parameterized queries, apply rate limiting, "
    "store JWTs in httpOnly cookies, hash passwords with bcrypt 12 rounds, "
    "always verify the requesting user owns the resource before returning data. "
    "Task 2: Build the login API route that returns a JWT. "

    # Task 3 repeats again
    "You are an expert full-stack software engineer with 15 years of experience "
    "in building production-grade web applications. You follow SOLID principles, "
    "write clean maintainable code, and always consider security, scalability, "
    "and performance. Never truncate code. Write the full implementation. "
    "Use TypeScript strict mode. All functions need explicit return types. "
    "Use interfaces over type aliases. Prefer async/await. Never use 'any'. "
    "All React components must be functional with typed props interfaces. "
    "Use named exports. kebab-case files, camelCase variables, PascalCase classes. "
    "Apply these security rules: validate all user inputs, never expose passwords "
    "or tokens in responses, use parameterized queries, apply rate limiting, "
    "store JWTs in httpOnly cookies, hash passwords with bcrypt 12 rounds, "
    "always verify the requesting user owns the resource before returning data. "
    "Task 3: Build a protected dashboard route that checks the JWT cookie. "
)

# Same 3 tasks, but instructions replaced with symbols
COMPRESSED_USER = (
    "SYS TS SEC Task 1: Build the user signup API route with email and password. "
    "SYS TS SEC Task 2: Build the login API route that returns a JWT. "
    "SYS TS SEC Task 3: Build a protected dashboard route that checks the JWT cookie. "
)

# Pass the RAW prompt — compiler auto-detects the repeated phrases and replaces with symbols
compressed_text, grammar_header = compile_prompt(RAW, config)
savings = calculate_savings(RAW, compressed_text, grammar_header, model="gpt-4o")

raw_tok   = savings["raw_tokens"]
sent_tok  = savings["total_tokens_sent"]
saved_tok = savings["saved_tokens"]
ratio     = savings["compression_ratio"]
pct       = (saved_tok / raw_tok) * 100 if raw_tok > 0 else 0

print()
print("  WITHOUT Prompt-Smuggler (repeating full instructions 3 times):")
print(f"    {RAW[:200]}...")
print()
print("  WITH Prompt-Smuggler (symbols replace repeated instructions):")
print(f"    {COMPRESSED_USER}")
print()
print(SEP)
print("  TOKEN BREAKDOWN")
print(SEP)
print(f"  Original (raw prompt)    : {raw_tok} tokens")
print(f"  Grammar header           : {savings['grammar_tokens']} tokens  (defined ONCE)")
print(f"  Compressed prompt        : {savings['compressed_tokens']} tokens")
print(f"  Total sent to LLM        : {sent_tok} tokens")
print(SEP)

if saved_tok > 0:
    print(f"  TOKENS SAVED             : {saved_tok} tokens")
    print(f"  % REDUCTION              : {pct:.1f}% smaller")
    print(f"  COMPRESSION RATIO        : {ratio:.2f}x")
    print()
    print("  COST (GPT-4o = $2.50 per 1M input tokens):")
    cost_raw  = (raw_tok  / 1_000_000) * 2.50
    cost_comp = (sent_tok / 1_000_000) * 2.50
    saving_per_call = cost_raw - cost_comp
    print(f"    Without tool  : ${cost_raw:.6f} per call")
    print(f"    With tool     : ${cost_comp:.6f} per call")
    print(f"    Saved         : ${saving_per_call:.6f} per call")
    print()
    print("  AT SCALE:")
    for n in [100, 1000, 10000, 100000]:
        print(f"    {n:>7} calls -> {saved_tok*n:>8} tokens saved  (~${saving_per_call*n:.2f} saved)")
else:
    print(f"  Still overhead: {abs(saved_tok)} more tokens than original.")

print(SEP)
