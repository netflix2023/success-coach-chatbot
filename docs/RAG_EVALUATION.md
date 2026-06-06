# RAG Pipeline Evaluation: Syllabi & Catalog Data (Issue #20)

This document provides a technical evaluation of the Retrieval-Augmented Generation (RAG) pipeline designed to index and query course catalogs and syllabi at Dallas College.

---

## 1. Chunking Strategy

Standard course catalog records and syllabi are highly dense, structured documents. To preserve context and avoid chunk truncation, we employ a **hybrid chunking strategy**:

### A. Course Catalog Chunking (Semantic/Record-based)
*   **Method**: Direct parsing of individual JSON course objects instead of arbitrary token splitting.
*   **Rationale**: A course is an atomic unit. Splitting a single course description (e.g., COSC 1436) across two chunks would sever prerequisites from course descriptions.
*   **Chunk Format**:
    ```text
    Course: [Prefix] [Number] - [Title]
    Description: [Description Text]
    Prerequisites: [Prerequisite Courses]
    URL: [Official Catalog Link]
    ```

### B. Syllabus & General Page Chunking (Fixed-Size with Overlap)
*   **Method**: Recursive character splitting.
*   **Parameters**:
    *   **Chunk Size**: 800 characters (~150-200 words).
    *   **Chunk Overlap**: 150 characters (~30-40 words).
*   **Rationale**: Overlapping chunks ensure that search phrases occurring at a boundary are not split and lost during similarity computation.

---

## 2. Vector Embeddings Specification

*   **Model**: `all-MiniLM-L6-v2` (SentenceTransformers).
*   **Output Dimensions**: 384 dimensions.
*   **Pros**:
    *   **Resource-Efficient**: Lightweight model, running fast on CPU environments (critical for Chromebook/Penguin resource constraints).
    *   **High Performance**: Strong semantic capturing for search queries compared to larger models (e.g., standard text-embedding-ada-002).
*   **Cons**:
    *   **Input Token Limit**: Max sequence length is 256 tokens. Texts exceeding this length are truncated during vector generation. 
    *   *Mitigation*: Pre-chunking long syllabi to ensure no chunk exceeds 200 words.

---

## 3. Retrieval & Similarity Thresholds

The retrieval pipeline executes a cosine similarity search on the embedded text vectors:

```text
Cosine Distance: d = 1 - (A · B) / (||A|| ||B||)
```

### Critical Tuning Parameters
*   **Top-K Matches**: Set to `top_k = 3`. 
    *   *Rationale*: Three matches provide enough context for the LLM without exceeding context windows or causing "Lost in the Middle" attention degradation.
*   **Similarity Threshold**: Set to `0.6` (for Cosine Similarity).
    *   *Query matches with similarity score < 0.6* are discarded.
    *   *Rationale*: Prevents irrelevant documents (noise) from polluting the LLM prompt when the student asks off-topic or general greeting questions.
