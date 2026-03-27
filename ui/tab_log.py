"""
ui/tab_log.py
-------------
Tab 3: Displays persistent send history with timestamp, recipient,
subject, job count, and status. Supports clearing the log.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from config.settings import COLOR
from data.log_manager import clear_log


class LogTab(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLOR["bg"], **kwargs)
        self._entries = []
        self._build()

    def _build(self):
        # Toolbar
        bar = tk.Frame(self, bg=COLOR["bg"], pady=10)
        bar.pack(fill="x", padx=16)

        tk.Label(bar, text="History of sent emails  (persisted across sessions)",
                 bg=COLOR["bg"], fg=COLOR["text_light"],
                 font=("Segoe UI", 9)).pack(side="left")

        tk.Button(bar, text="🗑  Clear Log", command=self._clear,
                  bg=COLOR["danger"], fg=COLOR["white"],
                  activebackground=COLOR["danger"], activeforeground=COLOR["white"],
                  relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"),
                  padx=6, pady=4, bd=0).pack(side="right")

        # Treeview
        style = ttk.Style()
        style.configure("Log.Treeview",
                        font=("Segoe UI", 9), rowheight=26,
                        background=COLOR["white"],
                        fieldbackground=COLOR["white"],
                        foreground=COLOR["text"])
        style.configure("Log.Treeview.Heading",
                        font=("Segoe UI", 9, "bold"),
                        background="#D5DDE8", foreground=COLOR["text"])
        style.map("Log.Treeview",
                  background=[("selected", COLOR["accent"])])

        cols = ("Timestamp", "Recipient", "Subject", "Jobs", "Status")
        self._tree = ttk.Treeview(self, columns=cols, show="headings",
                                  selectmode="browse", style="Log.Treeview")

        widths = {"Timestamp": 160, "Recipient": 220,
                  "Subject": 340, "Jobs": 60, "Status": 100}
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=widths[c], anchor="w")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 12), pady=8)
        self._tree.pack(fill="both", expand=True, padx=16, pady=(0, 12))

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh(self, entries: list):
        """Reload the treeview from a fresh list of log entries."""
        self._entries = entries
        for row in self._tree.get_children():
            self._tree.delete(row)

        for e in reversed(entries):
            tag = "sent" if e["status"] == "Sent" else "failed"
            self._tree.insert("", "end", values=(
                e["timestamp"], e["to"],
                e["subject"], e["jobs"], e["status"]
            ), tags=(tag,))

        self._tree.tag_configure("sent",   foreground=COLOR["success"])
        self._tree.tag_configure("failed", foreground=COLOR["danger"])

    # ── Actions ───────────────────────────────────────────────────────────────

    def _clear(self):
        if messagebox.askyesno("Clear Log", "Delete all send history?"):
            entries = clear_log()
            self.refresh(entries)
