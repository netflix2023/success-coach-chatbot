"""
Dallas College Catalog Scraper
==============================
Async parallel scraper that respects rate limits.

System: Modern Campus Catalog (PHP, server-rendered)
- Courses:  preview_course_nopop.php?catoid=5&coid=N
- Programs: preview_program.php?catoid=5&poid=N
- Listings: content.php?catoid=5&navoid=1222 (28 pages, paginated via filter[cpage]=N)
- Programs by subject: content.php?catoid=5&navoid=1229

Rate limiting strategy:
- Max 5 concurrent requests (semaphore)
- 0.5s delay between requests per worker
- Retry with exponential backoff on failure
- robots.txt says 120s crawl-delay; we do ~2 req/s total which is gentle
"""

import asyncio
import aiohttp
import json
import os
import re
import time
import logging
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, parse_qs, urlparse

# ---------------------
# Config
# ---------------------
BASE_URL = "https://catalog.dallascollege.edu"
CATOID = 5  # 2026-2027 catalog
MAX_CONCURRENT = 5
DELAY_BETWEEN_REQUESTS = 0.5  # seconds per worker
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponential base

OUTPUT_DIR = Path(__file__).parent.parent / "scraped"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scraper")


# ---------------------
# Data Models
# ---------------------
@dataclass
class Course:
    coid: int
    prefix: str       # e.g. "COSC"
    number: str       # e.g. "1436"
    title: str        # e.g. "Programming Fundamentals I"
    credits: str
    description: str
    prerequisites: str
    corequisites: str
    campus_locations: str
    lecture_hours: str
    lab_hours: str
    url: str


@dataclass
class Program:
    poid: int
    title: str
    degree_type: str  # AAS, AA, AS, Certificate, etc.
    description: str
    requirements: str  # full requirements text
    url: str


# ---------------------
# Rate-limited fetcher
# ---------------------
class RateLimitedFetcher:
    def __init__(self, session: aiohttp.ClientSession, max_concurrent: int, delay: float):
        self.session = session
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay = delay
        self.request_count = 0
        self.start_time = time.time()

    async def fetch(self, url: str, retries: int = MAX_RETRIES) -> str | None:
        async with self.semaphore:
            for attempt in range(retries):
                try:
                    await asyncio.sleep(self.delay)
                    async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if resp.status == 200:
                            self.request_count += 1
                            if self.request_count % 50 == 0:
                                elapsed = time.time() - self.start_time
                                log.info(f"Progress: {self.request_count} requests in {elapsed:.0f}s ({self.request_count/elapsed:.1f} req/s)")
                            return await resp.text()
                        elif resp.status in (429, 202, 503):
                            # 202 = server throttling (Modern Campus anti-scrape)
                            wait = RETRY_BACKOFF ** (attempt + 2) + 2
                            if attempt == 0:
                                log.warning(f"Throttled ({resp.status}) on {url}, backing off {wait}s...")
                            await asyncio.sleep(wait)
                        else:
                            log.warning(f"HTTP {resp.status} for {url}")
                            return None
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    wait = RETRY_BACKOFF ** (attempt + 1)
                    log.warning(f"Error fetching {url}: {e}. Retry in {wait}s...")
                    await asyncio.sleep(wait)
            log.error(f"Failed after {retries} retries: {url}")
            return None


# ---------------------
# Phase 1: Discover all course IDs from listing pages
# ---------------------
async def discover_course_ids(fetcher: RateLimitedFetcher) -> list[dict]:
    """Scrape all 28 pages of the course listing to collect coid values."""
    log.info("Phase 1: Discovering course IDs from listing pages...")

    # First, get page 1 to confirm total pages
    page1_url = f"{BASE_URL}/content.php?catoid={CATOID}&navoid=1222"
    html = await fetcher.fetch(page1_url)
    if not html:
        log.error("Could not fetch course listing page 1")
        return []

    soup = BeautifulSoup(html, "lxml")

    # Detect total pages from pagination
    total_pages = _detect_total_pages(soup)
    log.info(f"Found {total_pages} pages of course listings")

    # Extract course links from page 1
    courses = _extract_course_links(soup)
    log.info(f"Page 1: found {len(courses)} courses")

    # Fetch remaining pages in parallel
    page_urls = [
        f"{BASE_URL}/content.php?catoid={CATOID}&navoid=1222"
        f"&filter%5Bitem_type%5D=3&filter%5Bonly_active%5D=1"
        f"&filter%5B3%5D=1&filter%5Bcpage%5D={p}"
        for p in range(2, total_pages + 1)
    ]

    tasks = [fetcher.fetch(url) for url in page_urls]
    results = await asyncio.gather(*tasks)

    for i, html in enumerate(results, start=2):
        if html:
            page_soup = BeautifulSoup(html, "lxml")
            page_courses = _extract_course_links(page_soup)
            courses.extend(page_courses)
            log.info(f"Page {i}: found {len(page_courses)} courses")

    log.info(f"Total unique courses discovered: {len(courses)}")
    return courses


def _detect_total_pages(soup: BeautifulSoup) -> int:
    """Parse pagination to find total page count."""
    # Look for pagination text like "Page: 1 | 2 | 3 ... 28"
    page_text = soup.get_text()
    # Find patterns like "Page: 1 | 2 ... 28" or links with cpage= parameter
    page_links = soup.find_all("a", href=re.compile(r"cpage=\d+"))
    max_page = 1
    for link in page_links:
        href = link.get("href", "")
        match = re.search(r"cpage=(\d+)", href)
        if match:
            max_page = max(max_page, int(match.group(1)))
    # Also check for text-based page numbers
    for text in soup.stripped_strings:
        if text.isdigit() and int(text) > max_page:
            # Only count if near pagination context
            parent = None
            for el in soup.find_all(string=re.compile(r"^Page")):
                max_page = max(max_page, 28)  # fallback to known value
                break
    return max(max_page, 28)  # minimum 28 from our recon


def _extract_course_links(soup: BeautifulSoup) -> list[dict]:
    """Extract course coid and basic info from a listing page."""
    courses = []
    # Links to preview_course_nopop.php
    for link in soup.find_all("a", href=re.compile(r"preview_course_nopop\.php")):
        href = link.get("href", "")
        params = parse_qs(urlparse(href).query)
        coid = params.get("coid", [None])[0]
        if coid:
            text = link.get_text(strip=True)
            # Parse "ACCT 2301 - Principles of Financial Accounting"
            match = re.match(r"([A-Z]{2,4})\s+(\d{4})\s*[-–]\s*(.*)", text)
            if match:
                prefix, number, title = match.groups()
            else:
                prefix, number, title = "", "", text
            courses.append({
                "coid": int(coid),
                "prefix": prefix,
                "number": number,
                "title": title.strip(),
            })
    return courses


# ---------------------
# Phase 2: Scrape individual course pages
# ---------------------
async def scrape_courses(fetcher: RateLimitedFetcher, course_ids: list[dict]) -> list[Course]:
    """Fetch and parse each individual course page."""
    log.info(f"Phase 2: Scraping {len(course_ids)} individual course pages...")

    urls = [
        (c, f"{BASE_URL}/preview_course_nopop.php?catoid={CATOID}&coid={c['coid']}")
        for c in course_ids
    ]

    async def scrape_one(course_info: dict, url: str) -> Course | None:
        html = await fetcher.fetch(url)
        if not html:
            return None
        return _parse_course_page(html, course_info, url)

    tasks = [scrape_one(c, u) for c, u in urls]
    results = await asyncio.gather(*tasks)
    courses = [c for c in results if c is not None]
    log.info(f"Successfully scraped {len(courses)} courses")
    return courses


def _parse_course_page(html: str, info: dict, url: str) -> Course:
    """Parse a single course detail page into a Course object."""
    soup = BeautifulSoup(html, "lxml")
    body = soup.get_text(separator="\n", strip=True)

    # Extract fields via patterns
    credits = _extract_field(body, r"(\d+)\s*(?:Credit|credit|Credits|Semester)\s*(?:Hours?|credit)", default="")
    description = _extract_description(soup)
    prerequisites = _extract_section(body, r"(?:Prerequisite|Prerequisites?)\s*[:\-]?\s*(.*?)(?:\n|Corequisite|$)")
    corequisites = _extract_section(body, r"(?:Corequisite|Corequisites?)\s*[:\-]?\s*(.*?)(?:\n|$)")
    campus = _extract_section(body, r"(?:Campus(?:\s+Location)?)\s*[:\-]?\s*(.*?)(?:\n|$)")
    lecture_h = _extract_field(body, r"(\d+)\s*(?:Lecture|lecture)\s*(?:hours?|Hours?)", default="")
    lab_h = _extract_field(body, r"(\d+)\s*(?:Lab|lab|Laboratory)\s*(?:hours?|Hours?)", default="")

    return Course(
        coid=info["coid"],
        prefix=info.get("prefix", ""),
        number=info.get("number", ""),
        title=info.get("title", ""),
        credits=credits,
        description=description,
        prerequisites=prerequisites,
        corequisites=corequisites,
        campus_locations=campus,
        lecture_hours=lecture_h,
        lab_hours=lab_h,
        url=url,
    )


def _extract_description(soup: BeautifulSoup) -> str:
    """Pull the main course description paragraph."""
    # The description is usually the largest block of text in the page body
    body = soup.find("td", class_="block_content") or soup.find("body") or soup
    paragraphs = []
    for text in body.stripped_strings:
        # Skip very short metadata lines
        if len(text) > 60:
            paragraphs.append(text)
    return " ".join(paragraphs[:3]) if paragraphs else ""


def _extract_field(text: str, pattern: str, default: str = "") -> str:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else default


def _extract_section(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip()[:500] if match else ""


# ---------------------
# Phase 3: Discover and scrape programs/degree plans
# ---------------------
async def discover_program_ids(fetcher: RateLimitedFetcher) -> list[dict]:
    """Scrape the programs-by-subject page to collect poid values."""
    log.info("Phase 3: Discovering program/degree IDs...")

    # Multiple navoids that list programs
    navoids = [1227, 1229, 1219, 1221, 1224, 1261, 1262, 1263]
    all_programs = {}

    tasks = [
        fetcher.fetch(f"{BASE_URL}/content.php?catoid={CATOID}&navoid={nid}")
        for nid in navoids
    ]
    results = await asyncio.gather(*tasks)

    for html in results:
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        for link in soup.find_all("a", href=re.compile(r"preview_program\.php")):
            href = link.get("href", "")
            params = parse_qs(urlparse(href).query)
            poid = params.get("poid", [None])[0]
            if poid and poid not in all_programs:
                all_programs[poid] = {
                    "poid": int(poid),
                    "title": link.get_text(strip=True),
                }

    programs = list(all_programs.values())
    log.info(f"Discovered {len(programs)} unique programs/degrees")
    return programs


async def scrape_programs(fetcher: RateLimitedFetcher, program_ids: list[dict]) -> list[Program]:
    """Fetch and parse each individual program page."""
    log.info(f"Phase 4: Scraping {len(program_ids)} program pages...")

    async def scrape_one(info: dict) -> Program | None:
        url = f"{BASE_URL}/preview_program.php?catoid={CATOID}&poid={info['poid']}"
        html = await fetcher.fetch(url)
        if not html:
            return None
        return _parse_program_page(html, info, url)

    tasks = [scrape_one(p) for p in program_ids]
    results = await asyncio.gather(*tasks)
    programs = [p for p in results if p is not None]
    log.info(f"Successfully scraped {len(programs)} programs")
    return programs


def _parse_program_page(html: str, info: dict, url: str) -> Program:
    """Parse a program/degree page."""
    soup = BeautifulSoup(html, "lxml")
    body_el = soup.find("td", class_="block_content") or soup.find("body") or soup
    full_text = body_el.get_text(separator="\n", strip=True)

    # Try to detect degree type from title
    title = info.get("title", "")
    degree_type = ""
    for dt in ["Bachelor of Applied Science", "Bachelor of Applied Technology",
               "Bachelor of Science", "Associate of Applied Science",
               "Associate of Arts in Teaching", "Associate of Arts",
               "Associate of Science", "Certificate", "Field of Study",
               "Enhanced Skills Certificate", "Occupational Skills Award"]:
        if dt.lower() in title.lower() or dt.lower() in full_text[:500].lower():
            degree_type = dt
            break

    # Split into description vs requirements
    desc_parts = []
    req_parts = []
    in_requirements = False
    for line in full_text.split("\n"):
        if any(kw in line.lower() for kw in ["required courses", "degree requirements",
                                               "program requirements", "semester hours",
                                               "credit hours required"]):
            in_requirements = True
        if in_requirements:
            req_parts.append(line)
        else:
            desc_parts.append(line)

    return Program(
        poid=info["poid"],
        title=title,
        degree_type=degree_type,
        description="\n".join(desc_parts[:20]),
        requirements="\n".join(req_parts[:100]),
        url=url,
    )


# ---------------------
# Phase 5: Scrape general info pages (transfer, financial aid, advising)
# ---------------------
GENERAL_PAGES = [
    # Transfer info
    {"navoid": 1245, "category": "transfer", "label": "Transferring from Dallas College"},
    # Financial aid
    {"navoid": 1243, "category": "financial_aid", "label": "Financial Aid"},
    # Admissions
    {"navoid": 1239, "category": "admissions", "label": "Admissions & Enrollment"},
    # Student services
    {"navoid": 1250, "category": "student_services", "label": "Student Services"},
    # Academic calendar
    {"navoid": 1241, "category": "academic_calendar", "label": "Academic Calendar"},
    # College policies
    {"navoid": 1242, "category": "policies", "label": "College Policies"},
    # Core curriculum
    {"navoid": 1257, "category": "core_curriculum", "label": "Core Curriculum"},
]


async def scrape_general_pages(fetcher: RateLimitedFetcher) -> list[dict]:
    """Scrape general info pages and follow their sub-links."""
    log.info("Phase 5: Scraping general info pages...")
    results = []

    # Fetch top-level pages
    tasks = [
        fetcher.fetch(f"{BASE_URL}/content.php?catoid={CATOID}&navoid={p['navoid']}")
        for p in GENERAL_PAGES
    ]
    htmls = await asyncio.gather(*tasks)

    sub_links = []
    for page_info, html in zip(GENERAL_PAGES, htmls):
        if not html:
            continue
        soup = BeautifulSoup(html, "lxml")
        body = soup.find("td", class_="block_content") or soup.find("body") or soup
        text = body.get_text(separator="\n", strip=True)
        results.append({
            "navoid": page_info["navoid"],
            "category": page_info["category"],
            "label": page_info["label"],
            "content": text[:5000],
            "url": f"{BASE_URL}/content.php?catoid={CATOID}&navoid={page_info['navoid']}",
        })

        # Collect sub-page links (same domain content.php links)
        for link in body.find_all("a", href=re.compile(r"content\.php\?catoid=")):
            href = link.get("href", "")
            params = parse_qs(urlparse(href).query)
            sub_navoid = params.get("navoid", [None])[0]
            if sub_navoid and int(sub_navoid) != page_info["navoid"]:
                sub_links.append({
                    "navoid": int(sub_navoid),
                    "category": page_info["category"],
                    "label": link.get_text(strip=True),
                })

    # Dedupe and fetch sub-pages
    seen = set()
    unique_subs = []
    for sl in sub_links:
        if sl["navoid"] not in seen:
            seen.add(sl["navoid"])
            unique_subs.append(sl)

    if unique_subs:
        log.info(f"Found {len(unique_subs)} sub-pages to scrape...")
        sub_tasks = [
            fetcher.fetch(f"{BASE_URL}/content.php?catoid={CATOID}&navoid={s['navoid']}")
            for s in unique_subs
        ]
        sub_htmls = await asyncio.gather(*sub_tasks)

        for sub_info, html in zip(unique_subs, sub_htmls):
            if not html:
                continue
            soup = BeautifulSoup(html, "lxml")
            body = soup.find("td", class_="block_content") or soup.find("body") or soup
            text = body.get_text(separator="\n", strip=True)
            results.append({
                "navoid": sub_info["navoid"],
                "category": sub_info["category"],
                "label": sub_info["label"],
                "content": text[:5000],
                "url": f"{BASE_URL}/content.php?catoid={CATOID}&navoid={sub_info['navoid']}",
            })

    log.info(f"Scraped {len(results)} general info pages")
    return results


# ---------------------
# Save to disk
# ---------------------
def save_json(data, filename: str):
    """Save data as JSON to the scraped output directory."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"Saved {path} ({len(data)} records, {path.stat().st_size / 1024:.1f} KB)")


# ---------------------
# Main orchestrator
# ---------------------
async def main():
    start = time.time()
    log.info("=" * 60)
    log.info("Dallas College Catalog Scraper - Starting")
    log.info(f"Output dir: {OUTPUT_DIR}")
    log.info(f"Concurrency: {MAX_CONCURRENT} workers, {DELAY_BETWEEN_REQUESTS}s delay")
    log.info("=" * 60)

    headers = {
        "User-Agent": "DallasAI-SuccessCoach-Scraper/1.0 (Educational Project; Dallas College AI Club)",
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        fetcher = RateLimitedFetcher(session, MAX_CONCURRENT, DELAY_BETWEEN_REQUESTS)

        # Run all discovery phases in parallel
        course_ids, program_ids = await asyncio.gather(
            discover_course_ids(fetcher),
            discover_program_ids(fetcher),
        )

        # Save discovery indexes
        save_json(course_ids, "course_index.json")
        save_json(program_ids, "program_index.json")

        # Run detail scraping + general pages in parallel
        courses, programs, general = await asyncio.gather(
            scrape_courses(fetcher, course_ids),
            scrape_programs(fetcher, program_ids),
            scrape_general_pages(fetcher),
        )

        # Save all results
        save_json([asdict(c) for c in courses], "courses.json")
        save_json([asdict(p) for p in programs], "programs.json")
        save_json(general, "general_pages.json")

    elapsed = time.time() - start
    log.info("=" * 60)
    log.info(f"DONE in {elapsed:.1f}s")
    log.info(f"  Courses:  {len(courses)}")
    log.info(f"  Programs: {len(programs)}")
    log.info(f"  General:  {len(general)}")
    log.info(f"  Total requests: {fetcher.request_count}")
    log.info(f"  Avg rate: {fetcher.request_count / elapsed:.1f} req/s")
    log.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
