"""Quick test — score 10 jobs and send email alert"""
import json, sys
sys.path.insert(0, '.')

from ai.job_matcher import score_jobs, filter_top_matches
from notifications.email_alerts import send_job_alert

with open('data/latest_scrape.json') as f:
    jobs = json.load(f)

print(f"Loaded {len(jobs)} jobs")

# Normalize field names (Apify uses different keys)
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

# Show results
top = [j for j in scored if j.get("match_score", 0) >= 60]
print(f"\nTop matches (score >= 60): {len(top)}\n")

for j in scored:
    score = j.get("match_score", 0)
    emoji = "G" if score >= 80 else "Y" if score >= 60 else "R"
    title = j.get("title", "?")[:40]
    company = j.get("company", "?")[:20]
    print(f"  [{emoji}] {score:>3}/100 | {title:<40} | {company}")

# Send email
print("\nSending email digest...")
send_job_alert(top)

# Save results
with open("data/latest_results.json", "w") as f:
    json.dump(scored, f, indent=2, default=str)
print("Done! Results saved to data/latest_results.json")