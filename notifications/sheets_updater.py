"""
JobPilot — Google Sheets Tracker
Pushes matched jobs to a Google Sheet for tracking applications.

Setup:
  1. Go to https://console.cloud.google.com
  2. Create a project → Enable Google Sheets API & Google Drive API
  3. Create a Service Account → Download JSON credentials
  4. Save as credentials.json in the project root
  5. Share your Google Sheet with the service account email
     (the email looks like: xxx@xxx.iam.gserviceaccount.com)
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict
from datetime import datetime
from config.settings import GOOGLE_SHEETS_CREDS_FILE, GOOGLE_SHEET_NAME


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "Date Added", "Score", "Recommendation", "Title", "Company",
    "Location", "Salary", "Source", "Job Type", "AI Summary",
    "Match Reasons", "Missing Skills", "URL", "Applied?", "Cover Letter",
]


def _get_sheet():
    """Authenticate and return the worksheet."""
    creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)

    try:
        spreadsheet = gc.open(GOOGLE_SHEET_NAME)
        worksheet = spreadsheet.sheet1
    except gspread.SpreadsheetNotFound:
        # Create the spreadsheet if it doesn't exist
        spreadsheet = gc.create(GOOGLE_SHEET_NAME)
        worksheet = spreadsheet.sheet1
        # Add headers
        worksheet.append_row(HEADERS)
        # Format header row bold
        worksheet.format("A1:O1", {"textFormat": {"bold": True}})
        print(f"  📊 Created new Google Sheet: {GOOGLE_SHEET_NAME}")
        print(f"  ⚠️  Share this sheet with yourself to see it in your Google Drive!")

    return worksheet


def push_jobs_to_sheet(jobs: List[Dict]) -> int:
    """
    Append matched jobs to Google Sheet.
    Returns the number of rows added.
    """
    if not jobs:
        print("  📊 No jobs to push to Google Sheets.")
        return 0

    try:
        worksheet = _get_sheet()

        # Check if headers exist
        existing = worksheet.get_all_values()
        if not existing or existing[0] != HEADERS:
            worksheet.insert_row(HEADERS, 1)

        rows_added = 0
        for job in jobs:
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                job.get("match_score", 0),
                job.get("recommendation", "N/A"),
                job.get("title", "N/A"),
                job.get("company", "N/A"),
                job.get("location", "N/A"),
                job.get("salary", "N/A"),
                job.get("source", "N/A"),
                job.get("job_type", "N/A"),
                job.get("ai_summary", ""),
                ", ".join(job.get("match_reasons", [])),
                ", ".join(job.get("missing_skills", [])),
                job.get("url", ""),
                "No",  # Applied? — user fills this in manually
                job.get("cover_letter", "")[:5000],  # Sheets cell limit
            ]
            worksheet.append_row(row, value_input_option="USER_ENTERED")
            rows_added += 1

        print(f"  📊 Pushed {rows_added} jobs to Google Sheets")
        return rows_added

    except FileNotFoundError:
        print(f"  ❌ Google credentials file not found: {GOOGLE_SHEETS_CREDS_FILE}")
        print("     See README.md for setup instructions.")
        return 0
    except Exception as e:
        print(f"  ❌ Google Sheets error: {e}")
        return 0
