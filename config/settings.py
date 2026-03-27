"""
JobPilot — Centralized Configuration
All settings are loaded from environment variables (.env file)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Apify ───
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")

# ─── AI Provider (choose "groq" or "openai") ───
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")  # "groq" (free) or "openai" (paid)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model names
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ─── Google Sheets ───
GOOGLE_SHEETS_CREDS_FILE = os.getenv("GOOGLE_SHEETS_CREDS_FILE", "credentials.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "JobPilot Tracker")

# ─── Email Alerts ───
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Gmail App Password
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# ─── Job Search Preferences ───
JOB_KEYWORDS = os.getenv(
    "JOB_KEYWORDS",
    "Data Analyst, AI Analyst, Data Scientist, ML Engineer, Machine Learning"
)
JOB_LOCATION = os.getenv("JOB_LOCATION", "Boston, Massachusetts")
JOB_COUNTRY = os.getenv("JOB_COUNTRY", "usa")
DATE_POSTED_FILTER = os.getenv("DATE_POSTED_FILTER", "3days")  # "24hours", "3days", "week"
MAX_PAGES = int(os.getenv("MAX_PAGES", "2"))

# ─── Paths ───
SEEN_JOBS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "seen_jobs.json")
RESUME_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "my_resume.txt")

# ─── Scoring Threshold ───
MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "60"))  # 0-100, only alert if score >= this
