# Academic Data Mapping: Success Coach Chatbot (Issue #12)

This document provides a comprehensive map of the academic data sources used in the Success Coach Chatbot, detailing the scraped data structure and explaining how this raw data is transformed into a database schema for vector search in Neon Postgres.

---

## 1. Raw Data Sources (JSON Catalog)

The raw academic data is stored under `apps/data/scraped/` as static JSON files. These datasets are extracted directly from the official Dallas College course and program catalogs.

### A. Courses Schema (`courses.json`)
Describes individual academic courses, credits, descriptions, and prerequisites.
- **File Path**: `apps/data/scraped/courses.json`
- **Fields**:
  - `prefix` (String): Subject area abbreviation (e.g., `"COSC"`, `"ENGL"`).
  - `number` (String): Four-digit course number (e.g., `"1436"`, `"1301"`).
  - `title` (String): Full course title (e.g., `"Programming Fundamentals I"`).
  - `description` (String): Detailed catalog description of topics covered and TSI requirements.
  - `prerequisites` (String): List of prerequisite courses or eligibility rules.
  - `url` (String): URL pointing to the official catalog course page.

### B. Programs Schema (`programs.json`)
Describes academic programs, degrees (AS, AAS, AA), certificates, and requirement lists.
- **File Path**: `apps/data/scraped/programs.json`
- **Fields**:
  - `program_name` / `title` (String): Name of the degree/award (e.g., `"AS in Computer Science"`).
  - `description` / `content` (String): Summary of program goals and potential career paths.
  - `requirements` (String): Semester-by-semester breakdown of courses, hours, and electives.
  - `url` (String): URL pointing to the official catalog degree page.

### C. General Pages Schema (`general_pages.json`)
Covers non-course institutional information such as financial aid, residency rules, and policies.
- **File Path**: `apps/data/scraped/general_pages.json`
- **Fields**:
  - `title` (String): Title of the policy or page (e.g., `"Residency Classification"`).
  - `content` / `text` (String): Full parsed text of the policy.
  - `url` (String): URL pointing to the official page.

---

## 2. Database Schema Translation (Neon Postgres)

To enable fast vector search and metadata filtering in production, the raw JSON catalogs are mapped to a relational database schema using Prisma for **Neon Postgres** with the `pgvector` extension.

### A. Database Models

```prisma
// Prisma Schema Definition

model Course {
  id            String   @id @default(uuid())
  prefix        String   // e.g., "COSC"
  number        String   // e.g., "1436"
  title         String
  description   String   @db.Text
  prerequisites String?  @db.Text
  url           String
  embedding     Unsupported("vector(384)")? // MiniLM-L6-v2 vector representation
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  @@index([prefix, number])
}

model Program {
  id           String   @id @default(uuid())
  title        String
  description  String   @db.Text
  requirements String   @db.Text
  url          String
  embedding    Unsupported("vector(384)")? // MiniLM-L6-v2 vector representation
  createdAt    DateTime @default(now())
  updatedAt    DateTime @updatedAt
}

model PolicyPage {
  id        String   @id @default(uuid())
  title     String
  content   String   @db.Text
  url       String
  embedding Unsupported("vector(384)")? // MiniLM-L6-v2 vector representation
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
```

---

## 3. Embedding & Vector Mapping

- **Vector Dimension**: 384 dimensions.
- **Embedding Model**: `all-MiniLM-L6-v2` (SentenceTransformers).
- **Text Assembly for Ingestion**:
  - **Courses**: Embed `"{title} ({prefix} {number}): {description} Prerequisites: {prerequisites}"`.
  - **Programs**: Embed `"{title} Program: {description} Requirements: {requirements}"`.
  - **Policy Pages**: Embed `"{title}: {content}"`.
- **Query Pipeline**:
  1. The user inputs a natural language query (e.g., *"How many programming classes do I need for CS?"*).
  2. The Node.js API route vectorizes the query using the same `all-MiniLM-L6-v2` model (via an API endpoint or light microservice).
  3. The API runs a cosine similarity query against the Neon database:
     ```sql
     SELECT title, url, content, (1 - (embedding <=> $1)) AS similarity 
     FROM "Program" 
     WHERE (1 - (embedding <=> $1)) > 0.6
     ORDER BY similarity DESC 
     LIMIT 3;
     ```
  4. The top matches are fed into the LLM system prompt as the verified RAG context.
