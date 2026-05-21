import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import yaml
import re
import os

# Default configuration dictionary for demonstration/standalone fallback if no yaml config is found
DEFAULT_CONFIG = {
    "globals": {
        "µ_json": "Respond with a strictly valid JSON object, omitting any conversational filler or introductory markdown text.",
        "µ_style": "Use an authoritative, professional corporate tone, write in short punchy sentences, and always lead with a summary.",
        "Ξ_clean": "Remove all unnecessary inline comments, format using strict variable typing, and optimize loops for performance."
    }
}

class PromptSmugglerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🥷 Prompt-Smuggler (Desktop Client)")
        self.root.geometry("750x650")
        self.root.configure(bg="#1e1e2e")

        # Load rules from local config configuration if available
        self.config = self.load_config()

        self.setup_styles()
        self.create_widgets()

    def load_config(self):
        try:
            with open(".smugglerrc.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            try:
                with open(".smugglerrc.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return DEFAULT_CONFIG

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#1e1e2e', foreground='#cdd6f4')
        self.style.configure('TLabel', background='#1e1e2e', foreground='#cdd6f4', font=('Segoe UI', 10))
        self.style.configure('TButton', background='#11111b', foreground='#cdd6f4', borderwidth=0, font=('Segoe UI', 10, 'bold'))
        self.style.map('TButton', background=[('active', '#313244')])

    def create_widgets(self):
        # Top Header Banner Frame Accent
        header_frame = tk.Frame(self.root, bg="#11111b", height=60)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text="🥷 PROMPT-SMUGGLER COMPRESSOR", bg="#11111b", fg="#a6e3a1", font=("Segoe UI", 14, "bold"))
        header_label.pack(pady=15, padx=20, side="left")

        # Main Container Layout
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        # File Drop Zone Box
        self.drop_zone = tk.Label(
            main_frame,
            text="📂 Click to Browse or Select Text File Here",
            bg="#313244",
            fg="#bac2de",
            bd=2,
            relief="dashed",
            font=("Segoe UI", 11, "italic"),
            cursor="hand2"
        )
        self.drop_zone.pack(fill="x", ipady=25, pady=(0, 15))
        self.drop_zone.bind("<Button-1>", self.browse_file)

        # Input Text Editor
        input_lbl = ttk.Label(main_frame, text="Or Paste Your Raw Prompt Content Here:", font=("Segoe UI", 10, "bold"))
        input_lbl.pack(anchor="w", pady=(0, 5))

        self.input_text = tk.Text(main_frame, height=8, bg="#11111b", fg="#cdd6f4", insertbackground="white", bd=0, font=("Consolas", 10))
        self.input_text.pack(fill="x", pady=(0, 15))

        # Action Bar Frame
        btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=(0, 15))

        compress_btn = tk.Button(btn_frame, text="⚡ Compress Prompt", bg="#a6e3a1", fg="#11111b", activebackground="#94e2d5", activeforeground="#11111b", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=8, command=self.compress_text)
        compress_btn.pack(side="left")

        clear_btn = tk.Button(btn_frame, text="🗑️ Clear All", bg="#f38ba8", fg="#11111b", activebackground="#eba0ac", activeforeground="#11111b", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=8, command=self.clear_fields)
        clear_btn.pack(side="left", padx=10)

        self.metrics_lbl = ttk.Label(btn_frame, text="Active Mappings: Ready", font=("Segoe UI", 10, "italic"), foreground="#fab387")
        self.metrics_lbl.pack(side="right", pady=5)

        # Output Visual Text Windows
        output_lbl = ttk.Label(main_frame, text="Compressed Dynamic Output Block (Ready to Copy):", font=("Segoe UI", 10, "bold"))
        output_lbl.pack(anchor="w", pady=(0, 5))

        self.output_text = tk.Text(main_frame, height=12, bg="#11111b", fg="#94e2d5", insertbackground="white", bd=0, font=("Consolas", 10))
        self.output_text.pack(fill="both", expand=True, pady=(0, 10))

        copy_btn = tk.Button(main_frame, text="📋 Copy Output to Clipboard", bg="#89b4fa", fg="#11111b", activebackground="#b4befe", activeforeground="#11111b", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=8, command=self.copy_to_clipboard)
        copy_btn.pack(fill="x")

    def browse_file(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Markdown", "*.md"), ("All Files", "*.*")])
        if file_path:
            self.read_file_content(file_path)

    def read_file_content(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", content)
            filename = os.path.basename(path)
            self.drop_zone.config(text=f"📄 Loaded: {filename}", fg="#a6e3a1")
        except Exception as e:
            messagebox.showerror("Error Reading File", f"Could not open file:\n{str(e)}")

    def compress_text(self):
        raw_text = self.input_text.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Empty Content", "Please paste or select a text file to process.")
            return

        used_rules = {}
        compressed_text = raw_text

        # Match tokens parsed within the global mapping keys configuration
        for marker, blueprint in self.config.get("globals", {}).items():
            if marker in compressed_text:
                used_rules[marker] = blueprint

        # Bundle a clean structured header injection format blocks
        if used_rules:
            grammar_block = "<grammar>\n"
            for m, b in used_rules.items():
                grammar_block += f"{m}:{b}\n"
            grammar_block += "</grammar>\n\n"
            final_output = grammar_block + compressed_text
        else:
            final_output = compressed_text

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", final_output)

        savings_text = f"Analyzed Configuration Matrix | Active Rules Bundled: {len(used_rules)}"
        self.metrics_lbl.config(text=savings_text)

    def clear_fields(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.drop_zone.config(text="📂 Click to Browse or Select Text File Here", fg="#bac2de")
        self.metrics_lbl.config(text="Active Mappings: Ready")

    def copy_to_clipboard(self):
        out_content = self.output_text.get("1.0", tk.END).strip()
        if out_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(out_content)
            self.root.update()
            messagebox.showinfo("Success", "Prompt payload copied! Ready to paste into ChatGPT/Claude.")
        else:
            messagebox.showwarning("Empty Output", "Nothing to copy yet. Compress your prompt first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PromptSmugglerGUI(root)
    root.mainloop()
