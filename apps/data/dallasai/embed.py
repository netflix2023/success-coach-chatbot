"""
Chunking + ChromaDB Embedding Pipeline
=======================================
Processes scraped JSON → chunks → embeds into ChromaDB.
Runs incrementally: safe to re-run as new scraped data arrives.

Usage:
    python3 dallasai/embed.py

Output:
    scraped/chroma_db/       — ChromaDB persistent storage
    scraped/chunked_data.json — flat chunk list for inspection
"""

import json
import re
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("embed")

SCRAPED_DIR = Path(__file__).parent.parent / "scraped"
CHROMA_DIR = SCRAPED_DIR / "chroma_db"
COLLECTION_NAME = "dallas_college_catalog"

# Chunking config
CHUNK_SIZE = 700       # target tokens
CHUNK_OVERLAP = 70     # ~10% overlap
MIN_CHUNK_SIZE = 50
BATCH_SIZE = 100       # ChromaDB insert batch


# -----------------------------------
# 1. Chunking
# -----------------------------------
def estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 0.75))


def split_text(text: str) -> list[str]:
    """Split into overlapping chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+|\n{2,}|\n', text)
    chunks = []
    current = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sent_tokens = estimate_tokens(sentence)

        if current_tokens + sent_tokens > CHUNK_SIZE and current:
            chunks.append(" ".join(current))
            # Keep overlap
            overlap_tokens = 0
            overlap_start = len(current)
            for i in range(len(current) - 1, -1, -1):
                overlap_tokens += estimate_tokens(current[i])
                if overlap_tokens >= CHUNK_OVERLAP:
                    overlap_start = i
                    break
            current = current[overlap_start:]
            current_tokens = sum(estimate_tokens(s) for s in current)

        current.append(sentence)
        current_tokens += sent_tokens

    if current:
        chunks.append(" ".join(current))

    return [c for c in chunks if estimate_tokens(c) >= MIN_CHUNK_SIZE]


def build_course_text(course: dict) -> str:
    """Build rich text from a course record."""
    parts = []
    prefix = course.get("prefix", "")
    number = course.get("number", "")
    title = course.get("title", "")

    if prefix and number:
        parts.append(f"Course: {prefix} {number} — {title}")
    elif title:
        parts.append(f"Course: {title}")

    for field, label in [
        ("credits", "Credits"),
        ("campus_locations", "Campus Locations"),
        ("lecture_hours", "Lecture Hours"),
        ("lab_hours", "Lab Hours"),
    ]:
        val = course.get(field, "").strip()
        if val and val != "﻿":
            parts.append(f"{label}: {val}")

    if course.get("description"):
        parts.append(course["description"])
    if course.get("prerequisites"):
        parts.append(f"Prerequisites: {course['prerequisites']}")
    if course.get("corequisites"):
        parts.append(f"Corequisites: {course['corequisites']}")

    return "\n".join(parts)


def build_program_text(prog: dict) -> str:
    """Build rich text from a program record."""
    parts = [prog.get("title", "")]
    if prog.get("degree_type"):
        parts.append(f"Degree Type: {prog['degree_type']}")
    if prog.get("description"):
        parts.append(prog["description"])
    if prog.get("requirements"):
        parts.append(f"Requirements:\n{prog['requirements']}")
    return "\n".join(parts)


def chunk_all_data() -> list[dict]:
    """Load all scraped JSON and produce chunks with metadata."""
    all_chunks = []

    # --- Courses ---
    courses_path = SCRAPED_DIR / "courses.json"
    if courses_path.exists():
        courses = json.loads(courses_path.read_text())
        log.info(f"Chunking {len(courses)} courses...")
        for course in courses:
            text = build_course_text(course)
            for i, chunk_text in enumerate(split_text(text)):
                all_chunks.append({
                    "id": f"course_{course['coid']}_{i}",
                    "content": chunk_text,
                    "source_type": "course",
                    "source_id": str(course["coid"]),
                    "title": f"{course.get('prefix', '')} {course.get('number', '')} — {course.get('title', '')}".strip(" —"),
                    "url": course.get("url", ""),
                    "prefix": course.get("prefix", ""),
                    "number": course.get("number", ""),
                    "credits": course.get("credits", ""),
                })

    # --- Programs ---
    programs_path = SCRAPED_DIR / "programs.json"
    if programs_path.exists():
        programs = json.loads(programs_path.read_text())
        if programs:
            log.info(f"Chunking {len(programs)} programs...")
            for prog in programs:
                text = build_program_text(prog)
                for i, chunk_text in enumerate(split_text(text)):
                    all_chunks.append({
                        "id": f"program_{prog['poid']}_{i}",
                        "content": chunk_text,
                        "source_type": "program",
                        "source_id": str(prog["poid"]),
                        "title": prog.get("title", ""),
                        "url": prog.get("url", ""),
                        "degree_type": prog.get("degree_type", ""),
                    })

    # --- General pages ---
    general_path = SCRAPED_DIR / "general_pages.json"
    if general_path.exists():
        pages = json.loads(general_path.read_text())
        if pages:
            log.info(f"Chunking {len(pages)} general pages...")
            for page in pages:
                content = page.get("content", "")
                if not content:
                    continue
                for i, chunk_text in enumerate(split_text(content)):
                    all_chunks.append({
                        "id": f"general_{page['navoid']}_{i}",
                        "content": chunk_text,
                        "source_type": "general",
                        "source_id": str(page["navoid"]),
                        "title": page.get("label", ""),
                        "url": page.get("url", ""),
                        "category": page.get("category", ""),
                    })

    log.info(f"Total chunks: {len(all_chunks)}")
    return all_chunks


# -----------------------------------
# 2. ChromaDB Embedding
# -----------------------------------
def embed_chunks(chunks: list[dict]):
    """Insert chunks into ChromaDB with sentence-transformer embeddings."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions
    except ImportError:
        log.error("chromadb not installed. Run: pip3 install chromadb sentence-transformers")
        log.info("Saving chunked_data.json only (no embeddings).")
        return False

    log.info(f"Setting up ChromaDB at {CHROMA_DIR}...")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    # Use all-MiniLM-L6-v2 (384-dim, fast, good quality)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete and recreate to avoid stale data on re-run
    try:
        client.delete_collection(COLLECTION_NAME)
        log.info("Cleared existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Batch insert
    total = len(chunks)
    log.info(f"Embedding {total} chunks in batches of {BATCH_SIZE}...")
    start = time.time()

    for batch_start in range(0, total, BATCH_SIZE):
        batch = chunks[batch_start:batch_start + BATCH_SIZE]

        ids = [c["id"] for c in batch]
        documents = [c["content"] for c in batch]
        metadatas = []
        for c in batch:
            meta = {
                "source_type": c.get("source_type", ""),
                "source_id": c.get("source_id", ""),
                "title": c.get("title", ""),
                "url": c.get("url", ""),
            }
            # Add type-specific metadata
            for key in ["prefix", "number", "credits", "degree_type", "category"]:
                if c.get(key):
                    meta[key] = c[key]
            metadatas.append(meta)

        collection.add(ids=ids, documents=documents, metadatas=metadatas)

        done = min(batch_start + BATCH_SIZE, total)
        elapsed = time.time() - start
        rate = done / elapsed if elapsed > 0 else 0
        log.info(f"  {done}/{total} embedded ({rate:.0f} chunks/s)")

    elapsed = time.time() - start
    log.info(f"Embedding complete in {elapsed:.1f}s")

    # Verify
    count = collection.count()
    log.info(f"ChromaDB collection '{COLLECTION_NAME}' has {count} documents")

    # Test query
    log.info("Running test queries...")
    test_queries = [
        "What are the prerequisites for COSC 1436?",
        "How do I transfer to UT Dallas?",
        "Where is the success coaching office at Richland?",
        "What financial aid deadlines should I know?",
    ]
    for q in test_queries:
        results = collection.query(query_texts=[q], n_results=3)
        log.info(f"\n  Q: {q}")
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            score = 1 - dist  # cosine distance → similarity
            log.info(f"    [{i+1}] ({score:.3f}) {meta.get('title', '?')}")
            log.info(f"        {doc[:120]}...")

    return True


# -----------------------------------
# 3. Main
# -----------------------------------
def main():
    log.info("=" * 60)
    log.info("Chunking + Embedding Pipeline")
    log.info("=" * 60)

    # Step 1: Chunk
    chunks = chunk_all_data()

    if not chunks:
        log.error("No data to chunk. Run the scraper first.")
        return

    # Save chunked data JSON (always, regardless of ChromaDB)
    out_path = SCRAPED_DIR / "chunked_data.json"
    out_path.write_text(json.dumps(chunks, indent=2, ensure_ascii=False))
    log.info(f"Saved {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")

    # Print chunk stats
    by_type = {}
    sizes = []
    for c in chunks:
        t = c.get("source_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        sizes.append(estimate_tokens(c["content"]))

    log.info(f"Chunk breakdown:")
    for t, n in sorted(by_type.items()):
        log.info(f"  {t}: {n}")
    log.info(f"  avg size: {sum(sizes)//len(sizes)} tokens, range: {min(sizes)}-{max(sizes)}")

    # Step 2: Embed into ChromaDB
    embed_chunks(chunks)

    log.info("=" * 60)
    log.info("DONE")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
