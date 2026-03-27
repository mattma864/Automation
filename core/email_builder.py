"""
core/email_builder.py
----------------------
Builds email subject lines and bodies from job DataFrames.
"""

from datetime import date

import pandas as pd

from config.settings import (
    CC_ADDRESSES, COL_RESOLVE,
    EMAIL_COL_WIDTHS, EMAIL_TABLE_COLS,
)


def fmt_resolve(val) -> str:
    """Format a Resolve Date cell for display in the email body."""
    if pd.isna(val):
        return "Not scheduled"
    return pd.Timestamp(val).strftime("%m/%d/%Y") + "  * Past due"


def build_subject(job_count: int) -> str:
    word = "Job" if job_count == 1 else "Jobs"
    return f"[Action Required] Construction Pending — {job_count} {word} Awaiting Resolution"


def build_body(jobs: pd.DataFrame) -> str:
    n    = len(jobs)
    word = "job" if n == 1 else "jobs"

    header  = "  ".join(c.ljust(EMAIL_COL_WIDTHS[c]) for c in EMAIL_TABLE_COLS)
    divider = "  ".join("-" * EMAIL_COL_WIDTHS[c]    for c in EMAIL_TABLE_COLS)

    rows = []
    for _, row in jobs.iterrows():
        cells = []
        for c in EMAIL_TABLE_COLS:
            val = fmt_resolve(row[c]) if c == COL_RESOLVE else str(row[c])
            cells.append(val.ljust(EMAIL_COL_WIDTHS[c]))
        rows.append("  ".join(cells))

    table = "\n".join([header, divider] + rows)

    return (
        f"Hello,\n\n"
        f"You have {n} {word} currently flagged as Construction Pending "
        f"that require your attention.\n"
        f"Please review the details below and provide an update or coordinate "
        f"resolution at your earliest convenience.\n\n"
        f"{'─' * 95}\n{table}\n{'─' * 95}\n\n"
        f"If a Resolve Date is marked as past due, please escalate or confirm "
        f"a revised target date.\n\n"
        f"Thank you,\nAutomated Job Tracker\n"
        f"(Generated: {date.today().strftime('%B %d, %Y')})\n"
    )


def build_previews(grouped: dict) -> dict:
    """
    Build {poc: {"subject": str, "body": str}} for all stakeholders.
    grouped = {poc_email: DataFrame}
    """
    return {
        poc: {
            "subject": build_subject(len(jobs)),
            "body":    build_body(jobs),
        }
        for poc, jobs in grouped.items()
    }
