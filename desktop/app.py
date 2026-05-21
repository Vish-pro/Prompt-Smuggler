import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yaml
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "prompt-smuggler"))

try:
    from smuggler.compiler import compile_prompt, load_config
    from smuggler.tokenizer import calculate_savings
    SMUGGLER_AVAILABLE = True
except ImportError:
    SMUGGLER_AVAILABLE = False

DEFAULT_CONFIG = {
    "grammar": {
        "mu_json":  "Respond with a strictly valid JSON object, omitting any conversational filler or introductory markdown text.",
        "mu_style": "Use an authoritative, professional corporate tone, write in short punchy sentences, and always lead with a summary.",
        "Xi_clean": "Remove all unnecessary inline comments, format using strict variable typing, and optimize loops for performance."
    }
}

# Category colours for symbol chips
CATEGORY_COLORS = {
    "Formatting": "#cba6f7",   # mauve
    "Productivity": "#89b4fa", # blue
    "Content":    "#a6e3a1",   # green
    "Analysis":   "#fab387",   # peach
}

CATEGORY_ICONS = {
    "Formatting":  "[F]",
    "Productivity": "[P]",
    "Content":     "[C]",
    "Analysis":    "[A]",
}


def _categorise(key: str) -> str:
    if key.startswith(("mu_", "µ_", "Xi_", "Ξ_")):
        return "Formatting"
    if key in ("SIMPLE", "TLDR", "ACTION", "FIX", "EMAIL"):
        return "Productivity"
    if key in ("HOOK", "ELI5", "GHOST", "STREET"):
        return "Content"
    return "Analysis"


class PromptSmugglerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Prompt-Smuggler")
        self.root.geometry("1100x720")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        self.config = self._load_config()
        self.setup_styles()
        self.create_widgets()

    # ── Config ────────────────────────────────────────────────────────────────

    def _load_config(self):
        search_paths = [
            os.path.join(os.path.dirname(__file__), ".smugglerrc.yaml"),
            os.path.join(os.path.dirname(__file__), "..", "prompt-smuggler", ".smugglerrc.yaml"),
            ".smugglerrc.yaml",
        ]
        for path in search_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        loaded = yaml.safe_load(f)
                        if loaded:
                            return loaded
                except Exception:
                    pass
        return DEFAULT_CONFIG

    # ── Styles ────────────────────────────────────────────────────────────────

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".",         background="#1e1e2e", foreground="#cdd6f4")
        self.style.configure("TLabel",    background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("TButton",   background="#11111b", foreground="#cdd6f4", borderwidth=0, font=("Segoe UI", 10, "bold"))
        self.style.map("TButton",         background=[("active", "#313244")])
        self.style.configure("Lib.TFrame", background="#181825")
        self.style.configure("Cat.TLabel", background="#181825", foreground="#6c7086", font=("Segoe UI", 8, "bold"))

    # ── Widget layout ─────────────────────────────────────────────────────────

    def create_widgets(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg="#11111b", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header, text="  PROMPT-SMUGGLER",
            bg="#11111b", fg="#a6e3a1", font=("Segoe UI", 14, "bold")
        ).pack(pady=15, padx=20, side="left")

        self.status_dot = tk.Label(
            header, text="  READY",
            bg="#11111b", fg="#a6e3a1", font=("Segoe UI", 9)
        )
        self.status_dot.pack(pady=15, padx=20, side="right")

        # ── Body: left editor | right symbol library ───────────────────────
        body = tk.Frame(self.root, bg="#1e1e2e")
        body.pack(fill="both", expand=True)

        # Left column — editor
        left = tk.Frame(body, bg="#1e1e2e")
        left.pack(side="left", fill="both", expand=True, padx=(20, 8), pady=15)
        self._build_editor(left)

        # Right column — symbol library
        right = tk.Frame(body, bg="#181825", width=260)
        right.pack(side="right", fill="y", padx=(0, 12), pady=15)
        right.pack_propagate(False)
        self._build_symbol_library(right)

    # ── Left: editor ─────────────────────────────────────────────────────────

    def _build_editor(self, parent):
        # Drop zone
        self.drop_zone = tk.Label(
            parent,
            text="  Click to Browse or Drop a .txt / .md file here",
            bg="#313244", fg="#bac2de", bd=2, relief="solid",
            font=("Segoe UI", 11, "italic"), cursor="hand2", anchor="w"
        )
        self.drop_zone.pack(fill="x", ipady=14, pady=(0, 12))
        self.drop_zone.bind("<Button-1>", self.browse_file)

        ttk.Label(parent, text="Paste your raw prompt here:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.input_text = tk.Text(
            parent, height=9,
            bg="#11111b", fg="#cdd6f4",
            insertbackground="white", bd=0,
            font=("Consolas", 10), wrap="word"
        )
        self.input_text.pack(fill="x", pady=(0, 10))

        # Buttons
        btn_row = tk.Frame(parent, bg="#1e1e2e")
        btn_row.pack(fill="x", pady=(0, 10))

        tk.Button(
            btn_row, text="Compress Prompt",
            bg="#a6e3a1", fg="#11111b",
            activebackground="#94e2d5", activeforeground="#11111b",
            font=("Segoe UI", 10, "bold"), bd=0, padx=16, pady=8,
            command=self.compress_text
        ).pack(side="left")

        tk.Button(
            btn_row, text="Clear",
            bg="#f38ba8", fg="#11111b",
            activebackground="#eba0ac", activeforeground="#11111b",
            font=("Segoe UI", 10, "bold"), bd=0, padx=16, pady=8,
            command=self.clear_fields
        ).pack(side="left", padx=10)

        self.metrics_lbl = ttk.Label(
            btn_row, text="Tokens saved: --",
            font=("Segoe UI", 10, "italic"), foreground="#fab387"
        )
        self.metrics_lbl.pack(side="right", pady=5)

        ttk.Label(parent, text="Compressed output (ready to paste):", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 4))
        self.output_text = tk.Text(
            parent, height=10,
            bg="#11111b", fg="#94e2d5",
            insertbackground="white", bd=0,
            font=("Consolas", 10), wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, pady=(0, 10))

        tk.Button(
            parent, text="Copy to Clipboard -- Paste into Claude / ChatGPT / Any AI",
            bg="#89b4fa", fg="#11111b",
            activebackground="#b4befe", activeforeground="#11111b",
            font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=10,
            command=self.copy_to_clipboard
        ).pack(fill="x")

    # ── Right: symbol library ─────────────────────────────────────────────────

    def _build_symbol_library(self, parent):
        tk.Label(
            parent, text="SYMBOL LIBRARY",
            bg="#181825", fg="#cba6f7",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=12, pady=(12, 2))

        tk.Label(
            parent, text="Click any symbol to insert",
            bg="#181825", fg="#585b70",
            font=("Segoe UI", 8)
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # Scrollable canvas
        canvas = tk.Canvas(parent, bg="#181825", bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg="#181825")
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_resize)
        inner.bind("<Configure>", _on_frame_configure)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._populate_library(inner)

    def _populate_library(self, parent):
        grammar = self.config.get("grammar", {})
        if not grammar:
            tk.Label(parent, text="No grammar loaded.", bg="#181825", fg="#585b70",
                     font=("Segoe UI", 9)).pack(padx=12, pady=20)
            return

        # Group by category
        categories: dict[str, list] = {}
        for key, value in grammar.items():
            cat = _categorise(key)
            categories.setdefault(cat, []).append((key, value))

        for cat_order in ("Formatting", "Productivity", "Content", "Analysis"):
            if cat_order not in categories:
                continue
            entries = categories[cat_order]
            color = CATEGORY_COLORS[cat_order]
            icon  = CATEGORY_ICONS[cat_order]

            # Category header
            cat_frame = tk.Frame(parent, bg="#181825")
            cat_frame.pack(fill="x", padx=8, pady=(10, 2))

            tk.Label(
                cat_frame, text=f"{icon} {cat_order.upper()}",
                bg="#181825", fg=color,
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w")

            tk.Frame(cat_frame, bg=color, height=1).pack(fill="x", pady=(2, 0))

            # Symbol chips
            for key, value in entries:
                self._make_chip(parent, key, value, color)

    def _make_chip(self, parent, key: str, value: str, color: str):
        chip = tk.Frame(parent, bg="#313244", cursor="hand2")
        chip.pack(fill="x", padx=8, pady=3)

        # Symbol badge
        badge = tk.Label(
            chip, text=f" {key} ",
            bg=color, fg="#11111b",
            font=("Consolas", 9, "bold"),
            padx=4, pady=2
        )
        badge.pack(side="left", padx=(6, 6), pady=5)

        # Truncated description
        short = value if len(value) <= 55 else value[:52] + "..."
        desc = tk.Label(
            chip, text=short,
            bg="#313244", fg="#a6adc8",
            font=("Segoe UI", 8),
            anchor="w", justify="left", wraplength=155
        )
        desc.pack(side="left", fill="x", expand=True, pady=5, padx=(0, 6))

        # Tooltip on hover
        tip = tk.Label(
            self.root, text=value,
            bg="#45475a", fg="#cdd6f4",
            font=("Segoe UI", 8),
            wraplength=320, justify="left",
            padx=8, pady=6, relief="flat"
        )

        def _show_tip(event, w=tip):
            x = event.widget.winfo_rootx() - self.root.winfo_rootx() - 330
            y = event.widget.winfo_rooty() - self.root.winfo_rooty()
            if x < 5:
                x = event.widget.winfo_rootx() - self.root.winfo_rootx() + 20
            w.place(x=x, y=y)
            w.lift()

        def _hide_tip(event, w=tip):
            w.place_forget()

        # Click inserts the key at cursor position
        def _insert(event=None, k=key):
            pos = self.input_text.index(tk.INSERT)
            content = self.input_text.get("1.0", tk.END)
            # Add space before if cursor is not at start or after whitespace
            before = self.input_text.get("1.0", pos)
            prefix = " " if before and not before[-1].isspace() else ""
            self.input_text.insert(pos, f"{prefix}{k} ")
            self.input_text.focus_set()
            self.status_dot.config(text=f"  Inserted {k}", fg="#cba6f7")

        for widget in (chip, badge, desc):
            widget.bind("<Button-1>", _insert)
            widget.bind("<Enter>", _show_tip)
            widget.bind("<Leave>", _hide_tip)

        # Hover highlight
        def _enter(e):
            chip.config(bg="#45475a")
            badge.config(bg=color)
            desc.config(bg="#45475a")

        def _leave(e):
            chip.config(bg="#313244")
            badge.config(bg=color)
            desc.config(bg="#313244")

        for widget in (chip, badge, desc):
            widget.bind("<Enter>", lambda e, f=_enter, g=_show_tip: (f(e), g(e)))
            widget.bind("<Leave>", lambda e, f=_leave, g=_hide_tip: (f(e), g(e)))

    # ── Actions ───────────────────────────────────────────────────────────────

    def browse_file(self, event=None):
        path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("Markdown", "*.md"), ("All Files", "*.*")]
        )
        if path:
            self._load_file(path)

    def _load_file(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", content)
            self.drop_zone.config(text=f"  Loaded: {os.path.basename(path)}", fg="#a6e3a1")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def compress_text(self):
        raw = self.input_text.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showwarning("Empty", "Paste a prompt first.")
            return

        self.status_dot.config(text="  COMPRESSING...", fg="#fab387")
        self.root.update()

        if SMUGGLER_AVAILABLE:
            compressed_text, grammar_header = compile_prompt(raw, self.config)
            final = f"{grammar_header}\n\n{compressed_text}".strip() if grammar_header else compressed_text
            savings  = calculate_savings(raw, compressed_text, grammar_header)
            saved    = savings["saved_tokens"]
            raw_tok  = savings["raw_tokens"]
            sent     = savings["total_tokens_sent"]
            pct      = (saved / raw_tok * 100) if raw_tok > 0 else 0
        else:
            grammar = self.config.get("grammar", {})
            compressed_text = raw
            used = {}
            for key, value in grammar.items():
                if value in compressed_text:
                    compressed_text = compressed_text.replace(value, key)
                    used[key] = value
                elif key in compressed_text:
                    used[key] = value

            if used:
                lines = ["<grammar>"] + [f"{k}:{v}" for k, v in used.items()] + ["</grammar>"]
                header = "\n".join(lines)
                final = f"{header}\n\n{compressed_text}".strip()
            else:
                final = compressed_text

            raw_tok = len(raw.split())
            sent    = len(final.split())
            saved   = max(0, raw_tok - sent)
            pct     = (saved / raw_tok * 100) if raw_tok > 0 else 0

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", final)

        if saved > 0:
            self.metrics_lbl.config(
                text=f"Saved {saved} tokens  ({pct:.0f}% smaller)  {raw_tok} -> {sent}",
                foreground="#a6e3a1"
            )
            self.status_dot.config(text="  COMPRESSED", fg="#a6e3a1")
        else:
            self.metrics_lbl.config(
                text="No compression -- prompt already optimal.",
                foreground="#fab387"
            )
            self.status_dot.config(text="  READY", fg="#a6e3a1")

    def clear_fields(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.drop_zone.config(text="  Click to Browse or Drop a .txt / .md file here", fg="#bac2de")
        self.metrics_lbl.config(text="Tokens saved: --", foreground="#fab387")
        self.status_dot.config(text="  READY", fg="#a6e3a1")

    def copy_to_clipboard(self):
        out = self.output_text.get("1.0", tk.END).strip()
        if not out:
            messagebox.showwarning("Nothing to copy", "Compress a prompt first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(out)
        self.root.update()
        self.status_dot.config(text="  COPIED", fg="#89b4fa")
        messagebox.showinfo("Copied!", "Compressed prompt copied.\nPaste into Claude, ChatGPT, Gemini, or any AI.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PromptSmugglerGUI(root)
    root.mainloop()
