import os
import glob


def audit_grammar(grammar: dict, scan_dir: str = ".") -> dict:
    """
    Scans all .txt and .md files in scan_dir for symbol usage.
    Returns a report dict: {symbol: {definition, used_in, times_found}}.
    """
    # Collect all prompt-like files to scan
    files = []
    for ext in ("*.txt", "*.md", "*.prompt"):
        files.extend(glob.glob(os.path.join(scan_dir, "**", ext), recursive=True))

    report = {}
    for symbol, definition in grammar.items():
        found_in = []
        total = 0
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                count = content.count(symbol)
                if count > 0:
                    found_in.append((os.path.relpath(fpath, scan_dir), count))
                    total += count
            except Exception:
                continue

        report[symbol] = {
            "definition": definition[:80] + "..." if len(definition) > 80 else definition,
            "used_in": found_in,
            "times_found": total,
        }

    return report


def print_audit_report(report: dict) -> None:
    SEP = "-" * 65
    print(SEP)
    print("  PROMPT-SMUGGLER -- GRAMMAR AUDIT")
    print(SEP)

    used     = {k: v for k, v in report.items() if v["times_found"] > 0}
    unused   = {k: v for k, v in report.items() if v["times_found"] == 0}

    print(f"\n  ACTIVE symbols ({len(used)}):")
    if used:
        for symbol, data in used.items():
            print(f"\n    {symbol}  ({data['times_found']} uses)")
            print(f"      Definition : {data['definition']}")
            for fname, count in data["used_in"]:
                print(f"      Found in   : {fname} ({count}x)")
    else:
        print("    None found.")

    print(f"\n  DEAD symbols — never used ({len(unused)}):")
    if unused:
        for symbol, data in unused.items():
            print(f"\n    {symbol}  <-- REMOVE THIS")
            print(f"      Definition : {data['definition']}")
    else:
        print("    None. Your grammar is clean.")

    print()
    print(SEP)
