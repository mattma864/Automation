"""
ui/tab_preview.py
-----------------
Tab 2: Preview and edit each stakeholder's email before sending.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk

from config.settings import CC_ADDRESSES, COLOR


class PreviewTab(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLOR["bg"], **kwargs)
        self._grouped  = {}
        self._previews = {}
        self._poc_keys = []
        self._curr_poc = None
        self._build()

    def _build(self):
        # ── Left: stakeholder list ────────────────────────────────────────────
        left = tk.Frame(self, bg="#E8EDF2", width=250)
        left.pack(side="left", fill="y", padx=(12, 0), pady=12)
        left.pack_propagate(False)

        tk.Label(left, text="Stakeholders", bg="#E8EDF2",
                 fg=COLOR["text"], font=("Segoe UI", 10, "bold")
                 ).pack(pady=(12, 6), padx=10, anchor="w")

        tk.Label(left, text="Click a name to preview their email",
                 bg="#E8EDF2", fg=COLOR["text_light"],
                 font=("Segoe UI", 8), wraplength=220, justify="left"
                 ).pack(padx=10, anchor="w", pady=(0, 8))

        self._listbox = tk.Listbox(
            left, bg=COLOR["white"], fg=COLOR["text"], relief="flat",
            font=("Segoe UI", 10), selectbackground=COLOR["accent"],
            selectforeground=COLOR["white"], activestyle="none",
            borderwidth=0, highlightthickness=1,
            highlightbackground=COLOR["border"])
        self._listbox.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # ── Right: email editor ───────────────────────────────────────────────
        right = tk.Frame(self, bg=COLOR["bg"])
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        # Meta fields (TO / CC / SUBJECT)
        meta = tk.Frame(right, bg=COLOR["white"], relief="flat",
                        highlightbackground=COLOR["border"], highlightthickness=1)
        meta.pack(fill="x", pady=(0, 8))

        self._to_var   = tk.StringVar()
        self._cc_var   = tk.StringVar(value=CC_ADDRESSES)
        self._subj_var = tk.StringVar()

        for label, var in [("TO", self._to_var),
                            ("CC", self._cc_var),
                            ("SUBJECT", self._subj_var)]:
            row = tk.Frame(meta, bg=COLOR["white"])
            row.pack(fill="x", padx=12, pady=5)
            tk.Label(row, text=f"{label}:", bg=COLOR["white"],
                     fg=COLOR["text_light"], font=("Segoe UI", 9, "bold"),
                     width=8, anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var, bg=COLOR["white"], fg=COLOR["text"],
                     relief="flat", font=("Segoe UI", 10),
                     bd=0).pack(side="left", fill="x", expand=True)

        tk.Label(right,
                 text="Email Body  (editable — your changes apply only to this send)",
                 bg=COLOR["bg"], fg=COLOR["text_light"],
                 font=("Segoe UI", 9)).pack(anchor="w")

        self._body = scrolledtext.ScrolledText(
            right, font=("Courier New", 9), bg=COLOR["white"], fg=COLOR["text"],
            relief="flat", highlightbackground=COLOR["border"],
            highlightthickness=1, wrap="word", padx=10, pady=10)
        self._body.pack(fill="both", expand=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def load(self, grouped: dict, previews: dict):
        """Populate the stakeholder list from new data."""
        self._grouped  = grouped
        self._previews = previews
        self._poc_keys = list(grouped.keys())
        self._curr_poc = None

        self._listbox.delete(0, "end")
        for poc in self._poc_keys:
            n = len(grouped[poc])
            self._listbox.insert("end", f"  {poc}  ({n} job{'s' if n > 1 else ''})")

        # Clear editor
        self._to_var.set("")
        self._subj_var.set("")
        self._body.delete("1.0", "end")

    def get_edited(self, poc: str) -> dict:
        """
        Return the current editor content if poc is being previewed,
        otherwise return the stored preview (unedited).
        """
        if poc == self._curr_poc:
            return {
                "to":      self._to_var.get(),
                "cc":      self._cc_var.get(),
                "subject": self._subj_var.get(),
                "body":    self._body.get("1.0", "end").strip(),
            }
        p = self._previews.get(poc, {})
        return {
            "to":      poc,
            "cc":      CC_ADDRESSES,
            "subject": p.get("subject", ""),
            "body":    p.get("body", ""),
        }

    # ── Interaction ───────────────────────────────────────────────────────────

    def _on_select(self, event):
        sel = self._listbox.curselection()
        if not sel:
            return
        poc = self._poc_keys[sel[0]]
        self._curr_poc = poc
        p = self._previews.get(poc, {})

        self._to_var.set(poc)
        self._cc_var.set(CC_ADDRESSES)
        self._subj_var.set(p.get("subject", ""))
        self._body.delete("1.0", "end")
        self._body.insert("1.0", p.get("body", ""))
