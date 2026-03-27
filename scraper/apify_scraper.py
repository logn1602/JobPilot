"""
JobPilot — Multi-Platform Job Scraper via Apify
Supports: LinkedIn, Indeed, Glassdoor, Handshake
"""

from apify_client import ApifyClient
from config.settings import APIFY_API_TOKEN, JOB_KEYWORDS, JOB_LOCATION, JOB_COUNTRY, DATE_POSTED_FILTER, MAX_PAGES
from typing import List, Dict
import time


class JobScraper:
    """Scrapes job listings from multiple platforms using Apify Actors."""

    # ── Actor IDs on Apify Store (free, pay-per-compute) ──
    ACTORS = {
        "linkedin": "orgupdate/linkedin-jobs-scraper",
        "indeed": "misceres/indeed-scraper",
        "glassdoor": "radeance/glassdoor-jobs-scraper",
        "handshake": "orgupdate/handshake-jobs-scraper",
    }

    def __init__(self):
        if not APIFY_API_TOKEN:
            raise ValueError("APIFY_API_TOKEN not found! Get one free at https://console.apify.com")
        self.client = ApifyClient(APIFY_API_TOKEN)
        self.keywords = [kw.strip() for kw in JOB_KEYWORDS.split(",")]

    def scrape_all(self, platforms: List[str] = None) -> List[Dict]:
        """
        Scrape jobs from all specified platforms.
        Returns a unified list of job dicts.
        """
        if platforms is None:
            platforms = ["linkedin", "indeed", "glassdoor", "handshake"]

        all_jobs = []
        for platform in platforms:
            if platform not in self.ACTORS:
                print(f"  ⚠️  Unknown platform: {platform}, skipping...")
                continue
            try:
                print(f"  🔍 Scraping {platform.capitalize()}...")
                jobs = self._scrape_platform(platform)
                print(f"  ✅ {platform.capitalize()}: {len(jobs)} jobs found")
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"  ❌ {platform.capitalize()} scraper failed: {e}")

        return all_jobs

    def _scrape_platform(self, platform: str) -> List[Dict]:
        """Dispatch to the correct scraper based on platform."""
        actor_id = self.ACTORS[platform]

        if platform == "linkedin":
            return self._scrape_linkedin(actor_id)
        elif platform == "indeed":
            return self._scrape_indeed(actor_id)
        elif platform == "glassdoor":
            return self._scrape_glassdoor(actor_id)
        elif platform == "handshake":
            return self._scrape_handshake(actor_id)
        return []

    def _scrape_linkedin(self, actor_id: str) -> List[Dict]:
        """Scrape LinkedIn jobs."""
        run_input = {
            "countryName": JOB_COUNTRY,
            "locationName": JOB_LOCATION,
            "includeKeyword": ", ".join(self.keywords),
            "datePosted": DATE_POSTED_FILTER,
            "pagesToFetch": MAX_PAGES,
        }
        results = self._run_actor(actor_id, run_input)
        return [self._normalize(r, "LinkedIn") for r in results]

    def _scrape_indeed(self, actor_id: str) -> List[Dict]:
        """Scrape Indeed jobs using search URLs."""
        all_results = []
        for keyword in self.keywords[:3]:  # Limit to first 3 keywords to save credits
            search_url = (
                f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}"
                f"&l={JOB_LOCATION.replace(' ', '+')}&fromage=3"
            )
            run_input = {
                "startUrls": [{"url": search_url}],
                "maxItems": 25,
            }
            results = self._run_actor(actor_id, run_input)
            all_results.extend(results)
            time.sleep(2)  # Be polite between requests
        return [self._normalize(r, "Indeed") for r in all_results]

    def _scrape_glassdoor(self, actor_id: str) -> List[Dict]:
        """Scrape Glassdoor jobs."""
        all_results = []
        for keyword in self.keywords[:3]:
            run_input = {
                "keyword": keyword,
                "location": JOB_LOCATION,
                "max_items": 25,
                "job_posted": "7 days",
            }
            results = self._run_actor(actor_id, run_input)
            all_results.extend(results)
            time.sleep(2)
        return [self._normalize(r, "Glassdoor") for r in all_results]

    def _scrape_handshake(self, actor_id: str) -> List[Dict]:
        """Scrape Handshake jobs."""
        run_input = {
            "countryName": JOB_COUNTRY,
            "includeKeyword": ", ".join(self.keywords),
            "datePosted": DATE_POSTED_FILTER,
            "pagesToFetch": MAX_PAGES,
        }
        results = self._run_actor(actor_id, run_input)
        return [self._normalize(r, "Handshake") for r in results]

    def _run_actor(self, actor_id: str, run_input: dict) -> List[Dict]:
        """Run an Apify Actor and return the dataset items."""
        try:
            run = self.client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=300,
                memory_mbytes=256,  # Lower memory = fewer credits used
            )
            dataset_items = self.client.dataset(run["defaultDatasetId"]).list_items().items
            return dataset_items if dataset_items else []
        except Exception as e:
            print(f"    ⚠️  Actor {actor_id} error: {e}")
            return []

    def _normalize(self, raw: dict, source: str) -> Dict:
        """
        Normalize raw scraper output into a unified job format.
        Different platforms return different field names — this standardizes them.
        """
        # Try multiple field names for each attribute
        title = (
            raw.get("job_title")
            or raw.get("title")
            or raw.get("positionName")
            or raw.get("jobTitle")
            or "N/A"
        )
        company = (
            raw.get("company_name")
            or raw.get("company")
            or raw.get("companyName")
            or raw.get("employer", {}).get("name", "")
            if isinstance(raw.get("employer"), dict)
            else raw.get("company_name")
            or "N/A"
        )
        location = (
            raw.get("location")
            or raw.get("jobLocation")
            or raw.get("city", "")
            or "N/A"
        )
        url = (
            raw.get("URL")
            or raw.get("url")
            or raw.get("jobUrl")
            or raw.get("link")
            or raw.get("externalApplyLink")
            or ""
        )
        salary = (
            raw.get("salary")
            or raw.get("salaryText")
            or raw.get("salary", {}).get("salaryText", "")
            if isinstance(raw.get("salary"), dict)
            else raw.get("salary")
            or "Not listed"
        )
        description = (
            raw.get("description")
            or raw.get("descriptionText")
            or raw.get("jobDescription")
            or raw.get("job_description")
            or ""
        )
        posted_date = (
            raw.get("date")
            or raw.get("postedAt")
            or raw.get("posted_date")
            or raw.get("postedDate")
            or "N/A"
        )
        job_type = (
            raw.get("job_type")
            or raw.get("jobType")
            or raw.get("employmentType")
            or "N/A"
        )

        return {
            "title": str(title).strip(),
            "company": str(company).strip() if company else "N/A",
            "location": str(location).strip(),
            "salary": str(salary).strip() if salary else "Not listed",
            "url": str(url).strip(),
            "description": str(description).strip()[:3000],  # Cap at 3000 chars for AI input
            "posted_date": str(posted_date).strip(),
            "job_type": str(job_type).strip(),
            "source": source,
        }
