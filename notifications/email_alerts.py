"""
JobPilot — Email Alerts
Sends a daily digest email with matched jobs.

Setup:
  1. Go to https://myaccount.google.com/apppasswords
  2. Generate an App Password for "Mail"
  3. Set EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT in .env
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime
from config.settings import (
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT,
    SMTP_SERVER, SMTP_PORT,
)


def send_job_alert(jobs: List[Dict], subject_prefix: str = "JobPilot") -> bool:
    """
    Send an email digest of matched jobs.

    Args:
        jobs: List of scored job dicts
        subject_prefix: Prefix for the email subject line

    Returns:
        True if email sent successfully, False otherwise.
    """
    if not jobs:
        print("  📧 No jobs to email.")
        return False

    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT]):
        print("  ⚠️  Email credentials not configured. Skipping email alert.")
        print("     Set EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT in .env")
        return False

    try:
        # Build HTML email body
        html_body = _build_email_html(jobs)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚀 {subject_prefix}: {len(jobs)} New Job Matches — {datetime.now().strftime('%b %d, %Y')}"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECIPIENT

        # Plain text fallback
        plain_text = _build_email_plaintext(jobs)
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

        print(f"  📧 Email sent to {EMAIL_RECIPIENT} with {len(jobs)} job matches!")
        return True

    except Exception as e:
        print(f"  ❌ Email send failed: {e}")
        return False


def _build_email_html(jobs: List[Dict]) -> str:
    """Build a clean HTML email digest."""
    rows = ""
    for i, job in enumerate(jobs, 1):
        score = job.get("match_score", 0)
        color = "#27ae60" if score >= 80 else "#f39c12" if score >= 60 else "#e74c3c"
        rec = job.get("recommendation", "N/A")
        reasons = "<br>".join(f"• {r}" for r in job.get("match_reasons", []))
        missing = ", ".join(job.get("missing_skills", [])) or "None identified"

        rows += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 16px;">
                <div style="font-size: 14px; color: {color}; font-weight: bold;">
                    Score: {score}/100 — {rec}
                </div>
                <div style="font-size: 18px; font-weight: bold; margin: 4px 0;">
                    {i}. {job.get('title', 'N/A')}
                </div>
                <div style="color: #555; font-size: 14px;">
                    🏢 {job.get('company', 'N/A')} &nbsp;|&nbsp;
                    📍 {job.get('location', 'N/A')} &nbsp;|&nbsp;
                    💰 {job.get('salary', 'N/A')} &nbsp;|&nbsp;
                    🌐 {job.get('source', 'N/A')}
                </div>
                <div style="margin-top: 8px; font-size: 13px; color: #333;">
                    <strong>Why it's a match:</strong><br>{reasons}
                </div>
                <div style="margin-top: 4px; font-size: 13px; color: #888;">
                    <strong>Skills to brush up:</strong> {missing}
                </div>
                <div style="margin-top: 8px;">
                    <a href="{job.get('url', '#')}"
                       style="background: #2980b9; color: white; padding: 8px 16px;
                              text-decoration: none; border-radius: 4px; font-size: 13px;">
                        Apply Now →
                    </a>
                </div>
            </td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto;">
        <div style="background: #1a5276; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">🚀 JobPilot Daily Digest</h1>
            <p style="margin: 4px 0 0; font-size: 14px; opacity: 0.8;">
                {datetime.now().strftime('%B %d, %Y')} — {len(jobs)} new matches found
            </p>
        </div>
        <table style="width: 100%; border-collapse: collapse; background: white;">
            {rows}
        </table>
        <div style="text-align: center; padding: 16px; color: #999; font-size: 12px;">
            Powered by JobPilot — Your AI Job Search Automation Pipeline
        </div>
    </body>
    </html>
    """


def _build_email_plaintext(jobs: List[Dict]) -> str:
    """Build a plain text fallback."""
    lines = [f"JobPilot Daily Digest — {datetime.now().strftime('%B %d, %Y')}", "=" * 50, ""]
    for i, job in enumerate(jobs, 1):
        lines.append(f"{i}. {job.get('title', 'N/A')} @ {job.get('company', 'N/A')}")
        lines.append(f"   Score: {job.get('match_score', 0)}/100 | {job.get('recommendation', 'N/A')}")
        lines.append(f"   Location: {job.get('location', 'N/A')} | Salary: {job.get('salary', 'N/A')}")
        lines.append(f"   Source: {job.get('source', 'N/A')}")
        lines.append(f"   Apply: {job.get('url', 'N/A')}")
        lines.append("")
    return "\n".join(lines)
