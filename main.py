"""
╔═══════════════════════════════════════════════════════════════╗
║              JobPilot — Main Orchestrator                     ║
║   AI-Powered Job Search Automation Pipeline                   ║
║   by Shubh Dave | github.com/logn1602                         ║
╚═══════════════════════════════════════════════════════════════╝

Usage:
    python main.py                  # Run full pipeline (scrape → match → notify)
    python main.py --scrape-only    # Only scrape, no AI matching
    python main.py --score-only     # Score jobs from last scrape (data/latest_scrape.json)
    python main.py --reset          # Clear seen jobs history
    python main.py --platforms linkedin indeed   # Scrape specific platforms only
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.apify_scraper import JobScraper
from scraper.dedup import DedupTracker
from ai.job_matcher import score_jobs, filter_top_matches
from ai.cover_letter_gen import generate_cover_letter
from notifications.sheets_updater import push_jobs_to_sheet
from notifications.email_alerts import send_job_alert
from config.settings import MIN_MATCH_SCORE


LATEST_SCRAPE_FILE = os.path.join("data", "latest_scrape.json")
LATEST_RESULTS_FILE = os.path.join("data", "latest_results.json")


def run_pipeline(platforms=None, scrape_only=False, score_only=False):
    """Execute the full JobPilot pipeline."""

    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║           🚀 JobPilot Pipeline Starting...                ║")
    print(f"║           {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()

    # ── Step 1: Scrape ──
    if not score_only:
        print("━" * 55)
        print("STEP 1/5 — Scraping Job Boards")
        print("━" * 55)
        scraper = JobScraper()
        raw_jobs = scraper.scrape_all(platforms)
        print(f"\n  📦 Total raw jobs scraped: {len(raw_jobs)}")

        # Save raw scrape
        os.makedirs("data", exist_ok=True)
        with open(LATEST_SCRAPE_FILE, "w") as f:
            json.dump(raw_jobs, f, indent=2)
    else:
        print("━" * 55)
        print("STEP 1/5 — Loading Previous Scrape")
        print("━" * 55)
        try:
            with open(LATEST_SCRAPE_FILE, "r") as f:
                raw_jobs = json.load(f)
            print(f"  📦 Loaded {len(raw_jobs)} jobs from {LATEST_SCRAPE_FILE}")
        except FileNotFoundError:
            print("  ❌ No previous scrape found. Run without --score-only first.")
            return

    # ── Step 2: Deduplicate ──
    print(f"\n{'━' * 55}")
    print("STEP 2/5 — Deduplicating")
    print("━" * 55)
    tracker = DedupTracker()
    new_jobs = tracker.filter_new(raw_jobs)
    stats = tracker.get_stats()
    print(f"  🔄 {len(raw_jobs)} scraped → {len(new_jobs)} new (filtered {len(raw_jobs) - len(new_jobs)} duplicates)")
    print(f"  📊 Total unique jobs seen across all runs: {stats['total_seen']}")

    if not new_jobs:
        print("\n  ✅ No new jobs found since last run. All caught up!")
        return

    if scrape_only:
        print(f"\n  📝 Scrape-only mode: {len(new_jobs)} new jobs saved to {LATEST_SCRAPE_FILE}")
        return

    # ── Step 3: AI Scoring ──
    print(f"\n{'━' * 55}")
    print("STEP 3/5 — AI Job Matching")
    print("━" * 55)
    scored_jobs = score_jobs(new_jobs)
    top_matches = filter_top_matches(scored_jobs)
    print(f"\n  🎯 {len(top_matches)} jobs scored ≥ {MIN_MATCH_SCORE}/100")

    # Show quick summary
    for job in scored_jobs[:10]:
        emoji = "🟢" if job["match_score"] >= 80 else "🟡" if job["match_score"] >= 60 else "🔴"
        print(f"    {emoji} {job['match_score']:>3}/100 | {job['title'][:40]:<40} | {job['company'][:20]}")

    # ── Step 4: Generate Cover Letters for Top Matches ──
    print(f"\n{'━' * 55}")
    print("STEP 4/5 — Generating Cover Letters (Top Matches)")
    print("━" * 55)
    for job in top_matches[:5]:  # Generate for top 5 only (save API credits)
        print(f"    ✍️  Generating for: {job['title']} @ {job['company']}")
        cover_letter = generate_cover_letter(job)
        job["cover_letter"] = cover_letter

    # Save full results
    with open(LATEST_RESULTS_FILE, "w") as f:
        json.dump(scored_jobs, f, indent=2, default=str)

    # ── Step 5: Notify ──
    print(f"\n{'━' * 55}")
    print("STEP 5/5 — Sending Notifications")
    print("━" * 55)

    # Google Sheets
    push_jobs_to_sheet(top_matches)

    # Email digest
    send_job_alert(top_matches)

    # ── Summary ──
    print(f"\n{'━' * 55}")
    print("✅ PIPELINE COMPLETE")
    print("━" * 55)
    print(f"  📦 Jobs scraped:        {len(raw_jobs)}")
    print(f"  🆕 New (after dedup):   {len(new_jobs)}")
    print(f"  🎯 Top matches (≥{MIN_MATCH_SCORE}):   {len(top_matches)}")
    print(f"  ✍️  Cover letters:      {min(len(top_matches), 5)}")
    print(f"  💾 Full results:        {LATEST_RESULTS_FILE}")
    print()


def main():
    parser = argparse.ArgumentParser(description="JobPilot — AI Job Search Automation")
    parser.add_argument("--scrape-only", action="store_true", help="Only scrape, skip AI matching")
    parser.add_argument("--score-only", action="store_true", help="Score jobs from last scrape")
    parser.add_argument("--reset", action="store_true", help="Clear dedup history")
    parser.add_argument("--platforms", nargs="+", default=None,
                        choices=["linkedin", "indeed", "glassdoor", "handshake"],
                        help="Specific platforms to scrape")

    args = parser.parse_args()

    if args.reset:
        DedupTracker().reset()
        return

    run_pipeline(
        platforms=args.platforms,
        scrape_only=args.scrape_only,
        score_only=args.score_only,
    )


if __name__ == "__main__":
    main()
