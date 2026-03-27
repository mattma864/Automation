"""
ui/tab_jobs.py
--------------
Tab 1: Displays flagged jobs grouped by stakeholder.
Each stakeholder gets a card with a checkbox and a job table.
"""

import tkinter as tk
from tkinter import ttk

from config.settings import (
    COLOR, COL_ACTION, COL_DIVISION, COL_MAT, COL_NOTIF,
    COL_PM, COL_PROGRAM, COL_RESOLVE, COL_RESOURCE,
)
from core.email_builder import fmt_resolve


class JobsTab(tk.Frame):
    def __init__(self, parent, on_send_callback, **kwargs):
        super().__init__(parent, bg=COLOR["bg"], **kwargs)
        self.on_send = on_send_callback
        self.checks  = {}   # {poc: BooleanVar}
        self._build()

    def _build(self):
        # ── Toolbar ──────────────────────────────────────────────────────────
        bar = tk.Frame(self, bg=COLOR["bg"], pady=10)
        bar.pack(fill="x", padx=16)

        self.file_lbl = tk.Label(
            bar, text="No file selected", bg=COLOR["bg"],
            fg=COLOR["text_light"], font=("Segoe UI", 9), anchor="w")
        self.file_lbl.pack(side="left", padx=4)

        self._btn(bar, "✕  Deselect All", self._deselect_all,
                  COLOR["warning"], pad=6).pack(side="right", padx=4)
        self._btn(bar, "✓  Select All", self._select_all,
                  COLOR["success"], pad=6).pack(side="right", padx=4)

        # ── Scrollable cards area ─────────────────────────────────────────────
        outer = tk.Frame(self, bg=COLOR["bg"])
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        self._canvas = tk.Canvas(outer, bg=COLOR["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=COLOR["bg"])
        self._win   = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._win, width=e.width))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ── Send bar ──────────────────────────────────────────────────────────
        send_bar = tk.Frame(self, bg=COLOR["toolbar_bg"], pady=10)
        send_bar.pack(fill="x", side="bottom")

        self.send_count_lbl = tk.Label(
            send_bar, text="", bg=COLOR["toolbar_bg"],
            fg=COLOR["text"], font=("Segoe UI", 10))
        self.send_count_lbl.pack(side="left", padx=20)

        self._btn(send_bar, "🚀  Send Selected Emails", self._trigger_send,
                  COLOR["success"], pad=10, fsize=11).pack(side="right", padx=16)

    # ── Public API ────────────────────────────────────────────────────────────

    def render(self, grouped: dict, filepath: str):
        """Re-render cards from a new grouped dict."""
        for w in self._inner.winfo_children():
            w.destroy()
        self.checks = {}
        self.file_lbl.config(text=filepath)

        if not grouped:
            tk.Label(self._inner, text="No flagged jobs found.",
                     bg=COLOR["bg"], fg=COLOR["text_light"],
                     font=("Segoe UI", 11)).pack(pady=40)
        else:
            for poc, jobs in grouped.items():
                self._render_card(poc, jobs)

        self._update_count()

    def get_selected(self) -> list:
        return [poc for poc, v in self.checks.items() if v.get()]

    # ── Card rendering ────────────────────────────────────────────────────────

    def _render_card(self, poc, jobs):
        card = tk.Frame(self._inner, bg=COLOR["white"], relief="flat",
                        highlightbackground=COLOR["border"], highlightthickness=1)
        card.pack(fill="x", pady=6, padx=4)

        # Header row
        hdr = tk.Frame(card, bg=COLOR["sidebar"])
        hdr.pack(fill="x")

        var = tk.BooleanVar(value=True)
        self.checks[poc] = var
        var.trace_add("write", lambda *_: self._update_count())

        tk.Checkbutton(hdr, variable=var, bg=COLOR["sidebar"],
                       activebackground=COLOR["sidebar"], fg=COLOR["white"],
                       selectcolor=COLOR["accent_dark"],
                       relief="flat", bd=0).pack(side="left", padx=(10, 0), pady=8)

        tk.Label(hdr, text=f"  {poc}", bg=COLOR["sidebar"], fg=COLOR["white"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", pady=8)

        n = len(jobs)
        tk.Label(hdr, text=f"{n} job{'s' if n > 1 else ''}",
                 bg=COLOR["accent"], fg=COLOR["white"],
                 font=("Segoe UI", 9, "bold"),
                 padx=10, pady=4).pack(side="right", padx=12, pady=6)

        # Column header
        th = tk.Frame(card, bg=COLOR["header_bg"])
        th.pack(fill="x")
        for col, w in [("Program", 14), ("MAT", 10), ("PM#", 10),
                       ("Notification", 16), ("Division", 12),
                       ("Resource", 12), ("Resolve Date", 20), ("Action Needed", 0)]:
            tk.Label(th, text=col, bg=COLOR["header_bg"], fg=COLOR["text"],
                     font=("Segoe UI", 8, "bold"),
                     anchor="w", width=w).pack(side="left", padx=6, pady=4)

        # Job rows
        for i, (_, row) in enumerate(jobs.iterrows()):
            bg  = COLOR["white"] if i % 2 == 0 else COLOR["row_alt"]
            jr  = tk.Frame(card, bg=bg)
            jr.pack(fill="x")

            resolve_str = fmt_resolve(row[COL_RESOLVE])
            is_alert    = "Past due" in resolve_str or resolve_str == "Not scheduled"
            resolve_fg  = COLOR["danger"] if is_alert else COLOR["text"]

            for txt, w, fg in [
                (str(row[COL_PROGRAM]),  14, COLOR["text"]),
                (str(row[COL_MAT]),      10, COLOR["text"]),
                (str(row[COL_PM]),       10, COLOR["text"]),
                (str(row[COL_NOTIF]),    16, COLOR["text"]),
                (str(row[COL_DIVISION]), 12, COLOR["text"]),
                (str(row[COL_RESOURCE]), 12, COLOR["text"]),
                (resolve_str,            20, resolve_fg),
                (str(row[COL_ACTION]),    0, COLOR["text"]),
            ]:
                tk.Label(jr, text=txt, bg=bg, fg=fg,
                         font=("Segoe UI", 9), anchor="w",
                         width=w).pack(side="left", padx=6, pady=3)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_count(self):
        sel   = sum(1 for v in self.checks.values() if v.get())
        total = len(self.checks)
        self.send_count_lbl.config(
            text=f"{sel} of {total} stakeholder(s) selected for send")

    def _select_all(self):
        for v in self.checks.values(): v.set(True)

    def _deselect_all(self):
        for v in self.checks.values(): v.set(False)

    def _trigger_send(self):
        self.on_send(self.get_selected())

    def _btn(self, parent, text, cmd, color, pad=8, fsize=10):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=color, fg=COLOR["white"],
            activebackground=color, activeforeground=COLOR["white"],
            relief="flat", cursor="hand2",
            font=("Segoe UI", fsize, "bold"),
            padx=pad, pady=4, bd=0)
