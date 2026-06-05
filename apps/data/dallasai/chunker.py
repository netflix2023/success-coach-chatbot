"""
Chunker: Converts scraped JSON into embedding-ready chunks.
============================================================
Splits content into 500-1000 token chunks with 10% overlap,
ready for vector embedding and storage in Neon/pgvector.

Output: chunked_data.json - flat list of chunks with metadata.
"""

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

SCRAPED_DIR = Path(__file__).parent.parent / "scraped"
CHUNK_SIZE = 700       # target tokens per chunk
CHUNK_OVERLAP = 70     # ~10% overlap
MIN_CHUNK_SIZE = 50    # skip tiny chunks


@dataclass
class Chunk:
    id: str
    content: str
    source_type: str     # "course", "program", "general"
    source_id: str       # coid, poid, or navoid
    title: str
    url: str
    metadata: dict       # extra fields like prefix, credits, degree_type


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~0.75 tokens per word."""
    return int(len(text.split()) * 0.75)


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+|\n{2,}', text)
    chunks = []
    current = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sent_tokens = estimate_tokens(sentence)

        if current_tokens + sent_tokens > chunk_size and current:
            chunks.append(" ".join(current))
            # Keep overlap
            overlap_tokens = 0
            overlap_start = len(current)
            for i in range(len(current) - 1, -1, -1):
                overlap_tokens += estimate_tokens(current[i])
                if overlap_tokens >= overlap:
                    overlap_start = i
                    break
            current = current[overlap_start:]
            current_tokens = sum(estimate_tokens(s) for s in current)

        current.append(sentence)
        current_tokens += sent_tokens

    if current:
        chunks.append(" ".join(current))

    return [c for c in chunks if estimate_tokens(c) >= MIN_CHUNK_SIZE]


def chunk_courses() -> list[Chunk]:
    """Chunk course data - each course becomes 1-2 chunks."""
    path = SCRAPED_DIR / "courses.json"
    if not path.exists():
        return []

    courses = json.loads(path.read_text())
    chunks = []

    for course in courses:
        # Build a rich text representation
        parts = []
        if course.get("prefix") and course.get("number"):
            parts.append(f"{course['prefix']} {course['number']}: {course.get('title', '')}")
        elif course.get("title"):
            parts.append(course["title"])

        if course.get("credits"):
            parts.append(f"Credits: {course['credits']}")
        if course.get("campus_locations"):
            parts.append(f"Campus Locations: {course['campus_locations']}")
        if course.get("lecture_hours"):
            parts.append(f"Lecture Hours: {course['lecture_hours']}")
        if course.get("lab_hours"):
            parts.append(f"Lab Hours: {course['lab_hours']}")
        if course.get("description"):
            parts.append(f"Description: {course['description']}")
        if course.get("prerequisites"):
            parts.append(f"Prerequisites: {course['prerequisites']}")
        if course.get("corequisites"):
            parts.append(f"Corequisites: {course['corequisites']}")

        full_text = "\n".join(parts)
        text_chunks = split_text(full_text)

        for i, text in enumerate(text_chunks):
            chunk_id = f"course_{course['coid']}_{i}"
            chunks.append(Chunk(
                id=chunk_id,
                content=text,
                source_type="course",
                source_id=str(course["coid"]),
                title=f"{course.get('prefix', '')} {course.get('number', '')} - {course.get('title', '')}".strip(" -"),
                url=course.get("url", ""),
                metadata={
                    "prefix": course.get("prefix", ""),
                    "number": course.get("number", ""),
                    "credits": course.get("credits", ""),
                },
            ))

    return chunks


def chunk_programs() -> list[Chunk]:
    """Chunk program/degree data - larger programs get split."""
    path = SCRAPED_DIR / "programs.json"
    if not path.exists():
        return []

    programs = json.loads(path.read_text())
    chunks = []

    for prog in programs:
        parts = [prog.get("title", "")]
        if prog.get("degree_type"):
            parts.append(f"Degree Type: {prog['degree_type']}")
        if prog.get("description"):
            parts.append(prog["description"])
        if prog.get("requirements"):
            parts.append(f"Requirements:\n{prog['requirements']}")

        full_text = "\n".join(parts)
        text_chunks = split_text(full_text)

        for i, text in enumerate(text_chunks):
            chunk_id = f"program_{prog['poid']}_{i}"
            chunks.append(Chunk(
                id=chunk_id,
                content=text,
                source_type="program",
                source_id=str(prog["poid"]),
                title=prog.get("title", ""),
                url=prog.get("url", ""),
                metadata={
                    "degree_type": prog.get("degree_type", ""),
                },
            ))

    return chunks


def chunk_general() -> list[Chunk]:
    """Chunk general info pages."""
    path = SCRAPED_DIR / "general_pages.json"
    if not path.exists():
        return []

    pages = json.loads(path.read_text())
    chunks = []

    for page in pages:
        content = page.get("content", "")
        if not content:
            continue

        text_chunks = split_text(content)
        for i, text in enumerate(text_chunks):
            chunk_id = f"general_{page['navoid']}_{i}"
            chunks.append(Chunk(
                id=chunk_id,
                content=text,
                source_type="general",
                source_id=str(page["navoid"]),
                title=page.get("label", ""),
                url=page.get("url", ""),
                metadata={
                    "category": page.get("category", ""),
                },
            ))

    return chunks


def run_chunker():
    """Main entry: chunk all scraped data and save."""
    all_chunks = []
    all_chunks.extend(chunk_courses())
    all_chunks.extend(chunk_programs())
    all_chunks.extend(chunk_general())

    output_path = SCRAPED_DIR / "chunked_data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = [asdict(c) for c in all_chunks]
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    print(f"Chunked {len(all_chunks)} total chunks:")
    print(f"  Courses:  {sum(1 for c in all_chunks if c.source_type == 'course')}")
    print(f"  Programs: {sum(1 for c in all_chunks if c.source_type == 'program')}")
    print(f"  General:  {sum(1 for c in all_chunks if c.source_type == 'general')}")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    run_chunker()
