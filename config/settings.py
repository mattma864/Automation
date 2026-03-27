"""
config/settings.py
------------------
All user-configurable settings in one place.
Edit this file to adapt the tool to your sheet structure.

Source file layout:
  - Header row : 13  (data starts at row 14)
  - Col B  (idx  1)  : Notification
  - Col C  (idx  2)  : PM#
  - Col D  (idx  3)  : MAT
  - Col E  (idx  4)  : Program
  - Col F  (idx  5)  : Primary Hold-Up   ← trigger column
  - Col G  (idx  6)  : Resolve Date      ← date trigger column
  - Col W  (idx 22)  : Division
  - Col DD (idx 107) : Resource
  - Col DE (idx 108) : POC               ← stakeholder email
"""

# ── Excel read settings ───────────────────────────────────────────────────────

# Row number of the header (1-based as shown in Excel).
# Data is expected to start on the row immediately below.
HEADER_ROW = 13   # Excel row 13 = pandas header=12 (0-indexed)

# ── Column indices (0-based, matching Excel A=0, B=1, ...) ───────────────────
# These are used to locate columns by position, since the header row
# in your file may contain custom/merged text rather than clean names.

COL_IDX = {
    "Notification":    1,    # col B
    "PM#":             2,    # col C
    "MAT":             3,    # col D
    "Program":         4,    # col E
    "Primary Hold-Up": 5,    # col F  ← trigger
    "Resolve Date":    6,    # col G  ← date trigger
    "Division":       22,    # col W
    "Resource":      107,    # col DD
    "POC":           108,    # col DE ← stakeholder email, groups sends
}

# Friendly names — used throughout the app and in email output
COL_PROGRAM  = "Program"
COL_MAT      = "MAT"
COL_PM       = "PM#"
COL_NOTIF    = "Notification"
COL_DIVISION = "Division"
COL_RESOURCE = "Resource"
COL_POC      = "POC"
COL_HOLDUP   = "Primary Hold-Up"
COL_RESOLVE  = "Resolve Date"

# Action Needed is not a column in your file — it is always this fixed value
COL_ACTION         = "Action Needed"
ACTION_FIXED_VALUE = "Need Click Dates"

# ── Trigger logic ─────────────────────────────────────────────────────────────
# A job triggers an email when Primary Hold-Up matches TRIGGER_STATUS
# AND Resolve Date is blank OR in the past.

TRIGGER_STATUS = "Construction pending"

# ── Email settings ────────────────────────────────────────────────────────────

CC_ADDRESSES = "C7DB@PGE.com; K4AT@PGE.com; CZHD@PGE.com"

# Columns shown in the job table inside each email (in display order)
EMAIL_TABLE_COLS = [
    COL_PROGRAM,
    COL_MAT,
    COL_PM,
    COL_NOTIF,
    COL_DIVISION,
    COL_RESOURCE,
    COL_RESOLVE,
    COL_ACTION,
]

# Column display widths for the plain-text email table
EMAIL_COL_WIDTHS = {
    COL_PROGRAM:  10,
    COL_MAT:       8,
    COL_PM:        8,
    COL_NOTIF:    14,
    COL_DIVISION: 10,
    COL_RESOURCE: 10,
    COL_RESOLVE:  24,
    COL_ACTION:   18,
}

# ── Paths ─────────────────────────────────────────────────────────────────────

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs", "send_log.json")

# ── UI colors ─────────────────────────────────────────────────────────────────

COLOR = {
    "bg":          "#F4F6F9",
    "sidebar":     "#1E2D40",
    "accent":      "#2E86AB",
    "accent_dark": "#1A5C7A",
    "success":     "#27AE60",
    "warning":     "#E67E22",
    "danger":      "#E74C3C",
    "text":        "#2C3E50",
    "text_light":  "#7F8C8D",
    "white":       "#FFFFFF",
    "row_alt":     "#EAF2FB",
    "header_bg":   "#EAF0F6",
    "border":      "#CDD5DE",
    "toolbar_bg":  "#E8EDF2",
}
