"""Scan source URLs tu Google Sheet.

Sheet format: Column A = URL, Column B = status (empty = chua xu ly)
"""

import os
from typing import Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None


def get_sheet():
    """Connect to Google Sheet."""
    if not gspread:
        raise ImportError("gspread not installed. Run: pip install gspread google-auth")

    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID not set in .env")

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_file(creds_file, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id).sheet1


def scan_sources() -> list[dict]:
    """Doc sheet, tra ve list cac URL chua xu ly."""
    sheet = get_sheet()
    rows = sheet.get_all_values()

    candidates = []
    for i, row in enumerate(rows[1:], start=2):  # skip header
        url = row[0].strip() if row else ""
        status = row[1].strip() if len(row) > 1 else ""

        if url and not status:
            candidates.append({
                "url": url,
                "row": i,
            })

    return candidates


def mark_processed(row: int, status: str = "done"):
    """Danh dau URL da xu ly."""
    sheet = get_sheet()
    sheet.update_cell(row, 2, status)
