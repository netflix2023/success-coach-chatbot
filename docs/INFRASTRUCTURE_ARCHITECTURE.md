# Architectural Decision Record (ADR): Issue #10
> **Title**: Evaluation of 3rd-Party Free Tier Services & Agnostic LLM Architecture
> **Status**: APPROVED / FINALIZED
> **Date**: June 5, 2026
> **Deciders**: Dallas College AI Club (Engineering & Management Teams)

---

## 1. Context & Constraints

The Success Coach Chatbot must support the indexing of over 800 course catalogs and 300 academic degree program maps, delivering similarity-based answers to student questions in under **1.2 seconds**. 

As a student-led club project, we operate under a strict **$0.00/month budget** constraint. We must maximize free-tier cloud resources while maintaining a clean engineering path to scale to enterprise college servers in the future.

---

## 2. Database & Vector Storage Evaluation

We evaluated five database solutions for storing relational chat logs and 768-dimensional vector embeddings generated from catalog scraping:

| Service | Free Tier Capacity | Vector Support | Added Services | Key Limitations | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Supabase** | **500 MB DB / 1 GB Storage** | ✅ Yes (`pgvector`) | Auth, Realtime, Backups | Goes to sleep after 1 week inactivity | **SELECTED (Primary)** |
| **Neon Postgres** | 500 MB DB | ✅ Yes (`pgvector`) | None | Severe cold starts on serverless connection | Rejected (Backup) |
| **Convex** | 500 MB DB | ❌ No native ANN | Auth, Serverless Functions | Not suitable for RAG similarity indexing | Rejected |
| **Pinecone** | 2 GB storage | ✅ Yes (Native vector) | None | Separates data; double service configs | Rejected |
| **LanceDB** | Embedded/Local | ✅ Yes (Native vector) | None | Challenging to query concurrently from edge | Rejected |

### 🔍 Rationale: Why Supabase is Selected over Neon
1. **Unified File Storage**: Supabase includes **1 GB of free file storage**, allowing us to store raw scraped catalogs and PDF backups. Neon is database-only.
2. **Built-in Services**: Supabase provides built-in Authentication and Row-Level Security (RLS) out of the box, simplifying future student login expansions.
3. **No Connection Cold Starts**: Neon's compute lifecycle can introduce a 3–5 second cold-start latency if database connections are idle, violating our <1.2s response time target.

---

## 3. Web Hosting & Compute Evaluation

We evaluated three cloud hosting targets for deploying our Next.js frontend application and backend inference endpoints:

| Service | Free Tier Allowances | Key Benefits | Key Limitations | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Vercel** | **100 GB Bandwidth / mo** | Native Next.js support, Auto-SSL, edge routing | 10-second max function timeout | **SELECTED** |
| **Cloudflare** | Unlimited requests | Global edge hosting | No standard Node.js support (Edge only) | Rejected |
| **OCI (Oracle Cloud)**| 4 ARM Cores / 24 GB RAM | Always Free compute instances | High manual maintenance & DevOps complexity | Rejected |

### 🔍 Rationale: Why Vercel is Selected
Vercel allows us to deploy the Next.js UI and the `/api/chat` API routes together in a single monorepo deploy. This removes the need for a separate FastAPI backend server (avoiding multiple cold-start barriers) and leverages standard Next.js serverless routing.

---

## 4. LLM API Gateway & SDK Evaluation

We evaluated the choice between direct LLM APIs and an API Gateway proxy like OpenRouter:

| Option | Cost | Model Flexibility | Integration Complexity | Key Limitations | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenRouter** | **$0.00** (Free model list) | ✅ High (swaps Gemma, Qwen, Gemini Flash via config) | Low (OpenAI SDK standard) | Pre-auth credit limitations (402 error) | **SELECTED (Core Gateway)** |
| **Direct Gemini API** | **$0.00** | ❌ Low (locked to Google models) | Low (Google AI SDK) | Rate-limiting constraints (15 RPM) | **SELECTED (Primary Fallback)** |

### 🔍 Rationale: Why OpenRouter + Gemini Direct Fallback is Selected
1. **Vendor Agnosticism**: OpenRouter lets us swap models (e.g., Qwen 2, Gemma 2, Gemini Flash) without changing a single line of backend TS/JS code.
2. **Unified Client**: We use the standard Vercel AI SDK OpenAI provider pointing to OpenRouter's URL.
3. **Failover Safety**: If the OpenRouter free-tier quota is depleted or experiences rate limits, the Next.js chat route automatically falls back to invoking the direct Google Gemini API.

---

## 5. Engineering Guardrails & Token Preservation Protocols

To keep the application running permanently on the free tiers, we implement three mandatory protocols:

1. **Max Token Caps**: OpenRouter requests must explicitly define `max_tokens` (capped at **4,000 to 8,000**). This prevents OpenRouter from reserving massive credits and throwing a **402 Payment Required** error when balances are low.
2. **Edge Rate Limiting**: Next.js middleware enforces a rate limit of **5 requests per minute per IP address** using a local memory-based token bucket, protecting our free API rate ceilings.
3. **Supabase Sleep Awakening**: A GitHub Actions CRON workflow will ping the database once every 3 days with a lightweight query to prevent Supabase from going to sleep.
