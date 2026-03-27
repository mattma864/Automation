"""
ui/app.py
---------
Main application window. Wires together the three tabs and
orchestrates data loading, email sending, and log updates.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config.settings import CC_ADDRESSES, COLOR
from core.email_builder import build_previews
from core.filter import get_flagged, group_by_stakeholder, load_dataframe
from core.sender import send_outlook_email
from data.log_manager import append_entry, load_log
from ui.tab_jobs import JobsTab
from ui.tab_log import LogTab
from ui.tab_preview import PreviewTab


class EmailDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Construction Pending — Email Dashboard")
        self.geometry("1150x760")
        self.minsize(900, 600)
        self.configure(bg=COLOR["bg"])

        self._grouped  = {}
        self._previews = {}
        self._log      = load_log()

        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self, bg=COLOR["sidebar"], height=56)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="📋  Construction Pending  |  Email Dashboard",
                 bg=COLOR["sidebar"], fg=COLOR["white"],
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=20, pady=14)

        # Browse button in top bar
        tk.Button(top, text="📁  Browse File", command=self._load_file,
                  bg=COLOR["accent"], fg=COLOR["white"],
                  activebackground=COLOR["accent_dark"],
                  activeforeground=COLOR["white"],
                  relief="flat", cursor="hand2",
                  font=("Segoe UI", 10, "bold"),
                  padx=10, pady=4, bd=0).pack(side="left", padx=4, pady=14)

        self._status_lbl = tk.Label(
            top, text="No file loaded",
            bg=COLOR["sidebar"], fg="#AAB7C4",
            font=("Segoe UI", 10))
        self._status_lbl.pack(side="right", padx=20)

        # Notebook
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",      background=COLOR["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#D5DDE8", foreground=COLOR["text"],
                        font=("Segoe UI", 10, "bold"), padding=[16, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", COLOR["white"])],
                  foreground=[("selected", COLOR["accent"])])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self._tab_jobs    = JobsTab(nb, on_send_callback=self._confirm_send)
        self._tab_preview = PreviewTab(nb)
        self._tab_log     = LogTab(nb)

        nb.add(self._tab_jobs,    text="  📂  Jobs  ")
        nb.add(self._tab_preview, text="  ✉  Email Preview  ")
        nb.add(self._tab_log,     text="  📜  Send Log  ")

        # Populate log on start
        self._tab_log.refresh(self._log)

    # ── File loading ──────────────────────────────────────────────────────────

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Select Job Tracker Excel File",
            filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"),
                       ("All files", "*.*")])
        if not path:
            return

        try:
            df = load_dataframe(path)
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not read file:\n{e}")
            return

        flagged          = get_flagged(df)
        self._grouped    = group_by_stakeholder(flagged)
        self._previews   = build_previews(self._grouped)

        n_jobs = len(flagged)
        n_pocs = len(self._grouped)
        self._status_lbl.config(
            text=f"✓  {n_jobs} flagged job(s) across {n_pocs} stakeholder(s)")

        self._tab_jobs.render(self._grouped, path)
        self._tab_preview.load(self._grouped, self._previews)

    # ── Send flow ─────────────────────────────────────────────────────────────

    def _confirm_send(self, selected: list):
        if not selected:
            messagebox.showwarning(
                "Nothing selected",
                "Please check at least one stakeholder to send to.")
            return

        msg = (
            f"You are about to send emails to {len(selected)} stakeholder(s):\n\n"
            + "\n".join(f"  • {p}" for p in selected)
            + f"\n\nCC: {CC_ADDRESSES}\n\nProceed?"
        )
        if not messagebox.askyesno("Confirm Send", msg):
            return

        self._send_emails(selected)

    def _send_emails(self, pocs: list):
        sent, failed = [], []

        for poc in pocs:
            jobs   = self._grouped[poc]
            # Use live editor content if this POC is currently open in preview
            draft  = self._tab_preview.get_edited(poc)

            try:
                send_outlook_email(
                    to      = draft["to"],
                    cc      = draft["cc"],
                    subject = draft["subject"],
                    body    = draft["body"],
                )
                sent.append(poc)
                self._log = append_entry(
                    self._log, draft["to"], draft["subject"],
                    len(jobs), "Sent")
            except Exception as e:
                failed.append((poc, str(e)))
                self._log = append_entry(
                    self._log, poc, draft["subject"],
                    len(jobs), f"Failed: {e}")

        self._tab_log.refresh(self._log)

        summary = f"✓ Sent: {len(sent)}\n✗ Failed: {len(failed)}"
        if failed:
            summary += "\n\nFailed:\n" + "\n".join(f"  {p}: {e}" for p, e in failed)
            messagebox.showwarning("Send Complete", summary)
        else:
            messagebox.showinfo("Send Complete", summary)
