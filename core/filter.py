"""
core/filter.py
--------------
Logic for determining which jobs require an email.
Reads the source Excel by column index (position-based) since the
header row is row 13 and columns are identified by letter, not name.
"""

from datetime import date

import pandas as pd

from config.settings import (
    ACTION_FIXED_VALUE, COL_ACTION, COL_DIVISION, COL_HOLDUP,
    COL_IDX, COL_MAT, COL_NOTIF, COL_PM, COL_POC,
    COL_PROGRAM, COL_RESOLVE, COL_RESOURCE, HEADER_ROW,
    TRIGGER_STATUS,
)

# Columns we actually need to read (by index)
_USED_INDICES = list(COL_IDX.values())

# Map from friendly name → col index (for usecols + rename)
_IDX_TO_NAME  = {v: k for k, v in COL_IDX.items()}


def load_dataframe(filepath: str) -> pd.DataFrame:
    """
    Load the source Excel file.
    - Reads only the columns we need (by index)
    - Uses row HEADER_ROW as the header (0-indexed: HEADER_ROW - 1)
    - Renames columns to friendly names
    - Injects fixed Action Needed column
    - Parses Resolve Date
    """
    df = pd.read_excel(
        filepath,
        sheet_name=0,
        header=HEADER_ROW - 1,          # 0-indexed
        usecols=_USED_INDICES,
    )

    # Rename columns: whatever text was in the header row → friendly name
    # (we match by original position, not by header text)
    # Re-read with no header to get positional rename
    raw = pd.read_excel(
        filepath,
        sheet_name=0,
        header=None,
        skiprows=HEADER_ROW - 1,        # skip rows before header
        usecols=_USED_INDICES,
    )

    # Row 0 = header text from Excel, rows 1+ = data
    raw.columns = [_IDX_TO_NAME[i] for i in sorted(_USED_INDICES)]
    df = raw.iloc[1:].reset_index(drop=True)   # drop header row, reset index

    # Inject fixed Action Needed (not a real column)
    df[COL_ACTION] = ACTION_FIXED_VALUE

    # Parse resolve date
    df[COL_RESOLVE] = pd.to_datetime(df[COL_RESOLVE], errors="coerce")

    # Drop rows that are entirely empty (common in large tracker sheets)
    df.dropna(how="all", subset=[COL_HOLDUP, COL_POC], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def needs_email(row: pd.Series) -> bool:
    """
    Return True if a job row should trigger an email:
      - Primary Hold-Up == TRIGGER_STATUS
      - AND Resolve Date is blank OR in the past
    """
    if str(row[COL_HOLDUP]).strip() != TRIGGER_STATUS:
        return False
    resolve = row[COL_RESOLVE]
    if pd.isna(resolve):
        return True
    return resolve.date() < date.today()


def get_flagged(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows that need an email."""
    return df[df.apply(needs_email, axis=1)].copy()


def group_by_stakeholder(flagged: pd.DataFrame) -> dict:
    """Return {poc_email: DataFrame} grouped by POC column."""
    return dict(list(flagged.groupby(COL_POC)))
