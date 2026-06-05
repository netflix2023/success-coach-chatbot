"""
Resume scraper - picks up where the main scraper left off.
Uses lower concurrency (3 workers, 1.5s delay) to avoid 202 throttling.
Handles courses that were missed + all programs + general pages.
"""

import asyncio
import aiohttp
import json
import re
import sys
import time
import logging
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Add parent to path so dallasai package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
from dataclasses import asdict
from dallasai.scraper import _parse_course_page, _parse_program_page, GENERAL_PAGES

BASE_URL = "https://catalog.dallascollege.edu"
CATOID = 5
MAX_CONCURRENT = 3       # lower than main scraper
DELAY = 1.5              # more polite
MAX_RETRIES = 5           # more retries
RETRY_BACKOFF = 3

SCRAPED_DIR = Path(__file__).parent.parent / "scraped"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("resume")


class Fetcher:
    def __init__(self, session, max_concurrent, delay):
        self.session = session
        self.sem = asyncio.Semaphore(max_concurrent)
        self.delay = delay
        self.count = 0
        self.start = time.time()

    async def get(self, url: str) -> str | None:
        async with self.sem:
            for attempt in range(MAX_RETRIES):
                try:
                    await asyncio.sleep(self.delay)
                    async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as r:
                        if r.status == 200:
                            self.count += 1
                            if self.count % 20 == 0:
                                e = time.time() - self.start
                                log.info(f"  {self.count} fetched ({self.count/e:.1f}/s)")
                            return await r.text()
                        elif r.status in (202, 429, 503):
                            wait = RETRY_BACKOFF ** (attempt + 1) + 1
                            if attempt < 2:
                                log.warning(f"Throttled {r.status}, wait {wait}s (attempt {attempt+1})")
                            await asyncio.sleep(wait)
                        else:
                            return None
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    await asyncio.sleep(RETRY_BACKOFF ** (attempt + 1))
            return None


def _parse_course(html, info, url):
    """Same parser as main scraper."""
    return _parse_course_page(html, info, url)


def _parse_program(html, info, url):
    return _parse_program_page(html, info, url)


async def resume_courses(fetcher):
    """Scrape courses that were missed (got 202)."""
    index = json.loads((SCRAPED_DIR / "course_index.json").read_text())
    existing = json.loads((SCRAPED_DIR / "courses.json").read_text())
    done_coids = {c["coid"] for c in existing}
    missing = [c for c in index if c["coid"] not in done_coids]

    if not missing:
        log.info("All courses already scraped!")
        return existing

    log.info(f"Resuming {len(missing)} missing courses (of {len(index)} total)...")

    # Process in batches of 50 to save progress incrementally
    all_courses = list(existing)
    for batch_start in range(0, len(missing), 50):
        batch = missing[batch_start:batch_start + 50]
        tasks = []
        for c in batch:
            url = f"{BASE_URL}/preview_course_nopop.php?catoid={CATOID}&coid={c['coid']}"
            tasks.append((c, url))

        async def fetch_one(info, url):
            html = await fetcher.get(url)
            if not html:
                return None
            return asdict(_parse_course(html, info, url))

        results = await asyncio.gather(*[fetch_one(c, u) for c, u in tasks])
        new = [r for r in results if r is not None]
        all_courses.extend(new)

        # Save progress
        (SCRAPED_DIR / "courses.json").write_text(json.dumps(all_courses, indent=2, ensure_ascii=False))
        log.info(f"Batch done: +{len(new)} courses (total: {len(all_courses)})")

    return all_courses


async def scrape_programs(fetcher):
    """Scrape all programs from index."""
    index = json.loads((SCRAPED_DIR / "program_index.json").read_text())

    # Check for existing progress
    existing_path = SCRAPED_DIR / "programs.json"
    existing = json.loads(existing_path.read_text()) if existing_path.exists() else []
    done_poids = {p["poid"] for p in existing}
    missing = [p for p in index if p["poid"] not in done_poids]

    if not missing:
        log.info("All programs already scraped!")
        return existing

    log.info(f"Scraping {len(missing)} programs...")

    all_programs = list(existing)
    for batch_start in range(0, len(missing), 30):
        batch = missing[batch_start:batch_start + 30]

        async def fetch_one(info):
            url = f"{BASE_URL}/preview_program.php?catoid={CATOID}&poid={info['poid']}"
            html = await fetcher.get(url)
            if not html:
                return None
            return asdict(_parse_program(html, info, url))

        results = await asyncio.gather(*[fetch_one(p) for p in batch])
        new = [r for r in results if r is not None]
        all_programs.extend(new)

        (SCRAPED_DIR / "programs.json").write_text(json.dumps(all_programs, indent=2, ensure_ascii=False))
        log.info(f"Programs batch: +{len(new)} (total: {len(all_programs)})")

    return all_programs


async def scrape_general(fetcher):
    """Scrape general info pages + sub-pages."""
    log.info("Scraping general info pages...")
    results = []

    for page in GENERAL_PAGES:
        url = f"{BASE_URL}/content.php?catoid={CATOID}&navoid={page['navoid']}"
        html = await fetcher.get(url)
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        body = soup.find("td", class_="block_content") or soup.find("body") or soup
        text = body.get_text(separator="\n", strip=True)
        results.append({
            "navoid": page["navoid"],
            "category": page["category"],
            "label": page["label"],
            "content": text[:5000],
            "url": url,
        })

        # Collect sub-links
        for link in body.find_all("a", href=re.compile(r"content\.php\?catoid=")):
            href = link.get("href", "")
            params = parse_qs(urlparse(href).query)
            sub_navoid = params.get("navoid", [None])[0]
            if sub_navoid and int(sub_navoid) != page["navoid"]:
                sub_url = f"{BASE_URL}/content.php?catoid={CATOID}&navoid={sub_navoid}"
                sub_html = await fetcher.get(sub_url)
                if sub_html:
                    sub_soup = BeautifulSoup(sub_html, "lxml")
                    sub_body = sub_soup.find("td", class_="block_content") or sub_soup.find("body")
                    if sub_body:
                        results.append({
                            "navoid": int(sub_navoid),
                            "category": page["category"],
                            "label": link.get_text(strip=True),
                            "content": sub_body.get_text(separator="\n", strip=True)[:5000],
                            "url": sub_url,
                        })

    (SCRAPED_DIR / "general_pages.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    log.info(f"Scraped {len(results)} general pages")
    return results


async def main():
    start = time.time()
    log.info("=" * 50)
    log.info("Resume Scraper - picking up where we left off")
    log.info(f"Concurrency: {MAX_CONCURRENT}, Delay: {DELAY}s")
    log.info("=" * 50)

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        fetcher = Fetcher(session, MAX_CONCURRENT, DELAY)

        # Run sequentially to be gentle - courses first, then programs, then general
        courses = await resume_courses(fetcher)
        programs = await scrape_programs(fetcher)
        general = await scrape_general(fetcher)

    elapsed = time.time() - start
    log.info("=" * 50)
    log.info(f"DONE in {elapsed:.0f}s")
    log.info(f"  Courses:  {len(courses)}")
    log.info(f"  Programs: {len(programs)}")
    log.info(f"  General:  {len(general)}")
    log.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
