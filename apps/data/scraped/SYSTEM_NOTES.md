# Dallas College Catalog - Reverse Engineering Notes

## Platform
- **CMS**: Modern Campus Catalog™ (PHP, server-side rendered, jQuery)
- **Domain**: catalog.dallascollege.edu
- **Current Catalog**: catoid=5 (2026-2027)
- **Main site**: www.dallascollege.edu (separate CMS, likely TerminalFour based on robots.txt)

## URL Patterns

### Courses
- **Listing**: `content.php?catoid=5&navoid=1222` (28 pages, 100 courses/page = ~2784 total)
- **Pagination**: `&filter[item_type]=3&filter[only_active]=1&filter[3]=1&filter[cpage]=N`
- **Detail**: `preview_course_nopop.php?catoid=5&coid=NUMBER`

### Programs / Degrees
- **By Program**: `content.php?catoid=5&navoid=1227`
- **By Subject**: `content.php?catoid=5&navoid=1229`
- **By Award Type**: `content.php?catoid=5&navoid=1218`
- **AAS degrees**: navoid=1219
- **AAT degrees**: navoid=1224
- **Bachelor's**: navoid=1221
- **Emphasis**: navoid=1261
- **Engineering**: navoid=1262
- **Field of Study**: navoid=1263
- **Detail**: `preview_program.php?catoid=5&poid=NUMBER`

### General Info Navoids
- 1238: About / Home
- 1241: Academic Calendar
- 1242: College Policies
- 1243: Financial Aid
- 1245: Transfer Info
- 1250: Student Services
- 1257: Core Curriculum
- 1239: Admissions

## Anti-Scraping Behavior
- robots.txt: 120s crawl-delay for generic bots
- Returns HTTP 202 (Accepted) when rate limit hit — NOT a real 202, it's a throttle signal
- Triggers after ~800 requests at 2 req/s sustained
- Safe rate: ~0.5-1 req/s (3 concurrent workers, 1.5s delay)
- Blocks /ajax/ and /search_advanced.php

## Data Structure (per course page)
- Server-rendered HTML, no AJAX loading
- Course info in `<td class="block_content">`
- Fields: title, credits, campus locations, lecture/lab hours, description, prerequisites, corequisites
- No structured API — must parse HTML

## Key Numbers
- ~2,784 courses
- ~336 programs/degrees
- ~7 major info sections with sub-pages
