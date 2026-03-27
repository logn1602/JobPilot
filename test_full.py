"""Full test — score jobs, push to Google Sheets, and send email"""
import json, sys
sys.path.insert(0, '.')

from ai.job_matcher import score_jobs
from ai.cover_letter_gen import generate_cover_letter
from notifications.email_alerts import send_job_alert
from notifications.sheets_updater import push_jobs_to_sheet

with open('data/latest_scrape.json') as f:
    jobs = json.load(f)

print(f"Loaded {len(jobs)} jobs")

# Normalize field names
for j in jobs:
    if "URL" in j and "url" not in j:
        j["url"] = j["URL"]
    if "job_title" in j and "title" not in j:
        j["title"] = j["job_title"]
    if "company_name" in j and "company" not in j:
        j["company"] = j["company_name"]
    if not j.get("description"):
        j["description"] = j.get("job_description", "") or j.get("descriptionText", "") or ""

# Score first 10 jobs
print("\nScoring first 10 jobs with AI...\n")
scored = score_jobs(jobs[:10])

top = [j for j in scored if j.get("match_score", 0) >= 60]
print(f"\nTop matches: {len(top)}\n")

for j in scored:
    score = j.get("match_score", 0)
    emoji = "G" if score >= 80 else "Y" if score >= 60 else "R"
    title = j.get("title", "?")[:40]
    company = j.get("company", "?")[:20]
    print(f"  [{emoji}] {score:>3}/100 | {title:<40} | {company}")

# Generate cover letters for top 3
print("\nGenerating cover letters for top 3...")
for j in top[:3]:
    print(f"  Writing for: {j.get('title')} @ {j.get('company')}")
    j["cover_letter"] = generate_cover_letter(j)

# Push to Google Sheets
print("\nPushing to Google Sheets...")
push_jobs_to_sheet(top)

# Send email
print("\nSending email digest...")
send_job_alert(top)

print("\nDone!")