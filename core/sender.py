"""
core/sender.py
--------------
Handles sending emails via Outlook (win32com).
Windows only — requires: pip install pywin32
"""

import sys


def send_outlook_email(to: str, cc: str, subject: str, body: str) -> None:
    """
    Send a plain-text email via the locally installed Outlook client.
    Raises ImportError if pywin32 is not installed.
    Raises Exception if Outlook dispatch fails.
    """
    try:
        import win32com.client as win32
    except ImportError:
        raise ImportError(
            "pywin32 is required to send via Outlook.\n"
            "Install it with:  pip install pywin32"
        )

    outlook      = win32.Dispatch("outlook.application")
    mail         = outlook.CreateItem(0)
    mail.To      = to
    mail.CC      = cc
    mail.Subject = subject
    mail.Body    = body
    mail.Send()
