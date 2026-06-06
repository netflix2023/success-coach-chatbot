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

We evaluated vector database options for storing relational chat logs and 768-dimensional vector embeddings generated from catalog scraping across Prototyping and Production stages:

| Service | Capacity | Vector Support | Added Services | Key Limitations | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Neon Postgres** | **500 MB DB** | ✅ Yes (`pgvector`) | Autoscaling, Branching | Cold start compute latency | **SELECTED (Production)** |
| **ChromaDB** | Local / Disk | ✅ Yes (Native) | Light, Embedded | Local-only, not suited for multi-user web | **SELECTED (Prototyping)** |
| **Supabase** | 500 MB DB / 1 GB Storage | ✅ Yes (`pgvector`) | Auth, Realtime, Storage | Goes to sleep after 1 week inactivity | Rejected (Alternative) |
| **Convex** | 500 MB DB | ❌ No native ANN | Auth, Serverless Functions | Not suitable for RAG similarity indexing | Rejected |
| **Pinecone** | 2 GB storage | ✅ Yes (Native vector) | None | Separates data; double service configs | Rejected |
| **LanceDB** | Embedded/Local | ✅ Yes (Native vector) | None | Challenging to query concurrently from edge | Rejected |

### 🔍 Rationale: Why Neon Postgres & ChromaDB are Selected
1. **ChromaDB for Prototyping**: ChromaDB is embedded locally on developer machines and runs inside our Python/Streamlit script without setting up cloud accounts, allowing rapid iteration.
2. **Neon Postgres for Production**: Neon Postgres provides Postgres with `pgvector` out of the box, auto-scaling compute down to zero to fit free tier usage.
3. **Database Branching**: Neon's schema branching fits our collaborative workflow, enabling developers to test migrations on isolated database branches just like Git.
4. **Node.js/Prisma Compatibility**: Neon integrates cleanly with Prisma and Drizzle ORM to generate TypeScript definitions for the Node.js/React stack.

---

## 3. Web Hosting & Compute Evaluation

We evaluated cloud hosting targets for deploying our React frontend application and Node.js backend:

| Service | Free Tier Allowances | Key Benefits | Key Limitations | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Vercel** | **100 GB Bandwidth / mo** | Native React/Next.js hosting, auto-SSL, serverless functions | 10-second max function timeout | **SELECTED** |
| **Cloudflare** | Unlimited requests | Global edge hosting | Node.js compatibility challenges on workers | Rejected |
| **OCI (Oracle Cloud)**| 4 ARM Cores / 24 GB RAM | Always Free compute instances | High manual maintenance & DevOps complexity | Rejected |

### 🔍 Rationale: Why Vercel is Selected
Vercel allows us to deploy the React frontend and Node.js backend routes as serverless functions in a single deployment flow. This minimizes compute latency, simplifies deployment for student club members, and handles scaling out-of-the-box.

---

## 4. LLM API Gateway & SDK Evaluation

We evaluated the choice between direct LLM APIs and an API Gateway proxy like OpenRouter:

| Option | Cost | Model Flexibility | Integration Complexity | Key Limitations | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenRouter** | **$0.00** (Free model list) | ✅ High (swaps Gemma, Qwen, Gemini Flash via config) | Low (OpenAI SDK standard) | Pre-auth credit limitations (402 error) | **SELECTED (Core Gateway)** |
| **Direct Gemini API** | **$0.00** | ❌ Low (locked to Google models) | Low (Google AI SDK) | Rate-limiting constraints (15 RPM) | **SELECTED (Primary Fallback)** |

### 🔍 Rationale: Why OpenRouter + Gemini Direct Fallback is Selected
1. **Vendor Agnosticism**: OpenRouter lets us swap models (e.g., Qwen 2, Gemma 2, Gemini Flash) without changing a single line of backend Node.js code.
2. **Unified Client**: We use the standard OpenAI client SDK pointing to OpenRouter's proxy base URL.
3. **Failover Safety**: If the OpenRouter free-tier quota is depleted or experiences rate limits, the Node.js chat endpoint automatically falls back to invoking the direct Google Gemini API.

---

## 5. Engineering Guardrails & Token Preservation Protocols

To keep the application running permanently on the free tiers, we implement three mandatory protocols:

1. **Max Token Caps**: OpenRouter requests must explicitly define `max_tokens` (capped at **4,000 to 8,000**). This prevents OpenRouter from reserving massive credits and throwing a **402 Payment Required** error when balances are low.
2. **Rate Limiting**: The Node.js backend enforces a rate limit of **5 requests per minute per IP address** using a memory-based token bucket to protect our free API rate ceilings.
3. **Neon Cold-Start Mitigation**: Since Neon Postgres compute scales down to zero when idle, the first query after inactivity may experience a 3–5 second latency. To mitigate this:
   - The UI displays an active "Waking up database..." spinner during initial connection.
   - A background cron-ping checks the database status periodically to keep the instance warm during peak student hours.

