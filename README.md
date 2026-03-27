# Construction Pending — Email Dashboard

A tkinter desktop tool that reads your job tracker Excel file and sends
one consolidated Outlook email per stakeholder for all their pending jobs.

---

## Folder Structure

```
email_dashboard/
│
├── main.py                  ← Entry point — run this
│
├── config/
│   └── settings.py          ← Column names, trigger logic, CC addresses, colors
│
├── core/
│   ├── filter.py            ← Job filtering & stakeholder grouping
│   ├── email_builder.py     ← Subject line & body generation
│   └── sender.py            ← Outlook send via win32com
│
├── ui/
│   ├── app.py               ← Main window, wires everything together
│   ├── tab_jobs.py          ← Tab 1: flagged jobs with checkboxes
│   ├── tab_preview.py       ← Tab 2: editable email preview
│   └── tab_log.py           ← Tab 3: send history
│
├── data/
│   └── log_manager.py       ← Read/write send_log.json
│
├── logs/
│   └── send_log.json        ← Auto-created on first send
│
└── requirements.txt
```

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

1. Click **Browse File** in the top bar
2. Navigate to your OneDrive-synced folder and select the Excel file
3. **Jobs tab** — review flagged jobs, uncheck any stakeholders to skip
4. **Email Preview tab** — click a stakeholder to see/edit their draft email
5. Click **Send Selected Emails** → confirm → done
6. **Send Log tab** — see full history of all sends

---

## Trigger Logic

A job triggers an email when **both** conditions are true:
- `Primary Hold-Up` == `"Construction pending"`
- `Resolve Date` is blank **OR** is in the past

---

## Configuration

All settings live in `config/settings.py`:

| Setting | What it controls |
|---|---|
| `COL_*` variables | Column header names in your Excel sheet |
| `TRIGGER_STATUS` | The hold-up value that flags a job |
| `CC_ADDRESSES` | Fixed CC recipients on every email |
| `EMAIL_TABLE_COLS` | Which columns appear in the email table |
| `COLOR` | UI color scheme |
