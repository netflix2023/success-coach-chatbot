# Club Repository Code & Architecture Review
> **Document**: Evaluation of all commits, pull requests, and architectural discussions in the upstream club repository.
> **Date**: June 5, 2026
> **Reviewer**: AI Success Coach Chatbot Team

---

## 1. Review of Contributions by David Bracewell (`@dbracewell`)

### A. Monorepo Scaffolding (PR #17: `initial_commit`)
*   **Assessment**: The repository structure is set up as a standard monorepo dividing data processing and user interfaces cleanly:
    *   `apps/frontend/`: React application using Next.js 15, TypeScript, Tailwind CSS, Prettier, ESLint, and Shadcn UI.
    *   `apps/data/`: Isolated Python workspace managed via `uv` package manager with `pyproject.toml` and pytest structures.
*   **Feedback & Adjustments Made**:
    *   *Aesthetics & Typography*: The initial Next.js layout defaulted to standard system sans fonts. We modified `layout.tsx` to pull Google Fonts (`Outfit` and `Inter`) and modified `globals.css` to expose these variables to Tailwind for a premium feel.
    *   *Environment Configurations*: Added `.env.example` with Supabase and Gemini settings. We updated this file to include OpenRouter and Neon Postgres settings to match the final stack changes.

---

## 2. Review of Contributions by T.J. Chan (`@tjchan001`)

### A. Infrastructure Proposal (`upstream/tjchan001-patch-1`)
*   **Assessment**: T.J. proposed a serverless architecture in `docs/INFRASTRUCTURE_ARCHITECTURE.md` comparing Convex, Neon, Pinecone, and LanceDB.
*   **Proposed Stack**:
    *   *Frontend*: React on Vercel
    *   *Backend*: FastAPI (serverless)
    *   *Database*: Neon Postgres + pgvector
    *   *LLM Gateway*: OpenRouter (OpenAI-compatible SDK)
*   **Feedback & Alignment**:
    *   *FastAPI vs. Next.js/Node.js Backend*: T.J. proposed a FastAPI serverless backend. To simplify deployment, reduce multiple serverless cold starts, and keep the stack unified, the team decided to use a **Node.js backend** integrated with the **React frontend** hosted on **Vercel**.
    *   *Database Choice*: T.J.'s recommendation of **Neon Postgres** is excellent due to its autoscaling compute and database branching features. We have finalized Neon Postgres as our production database, with **ChromaDB** serving as our local prototyping database.
    *   *OpenRouter Integration*: T.J.'s suggestion of an OpenAI-compatible SDK pointing to OpenRouter is the correct path for vendor-agnostic swapping. We added a fallback protocol where the Node.js backend automatically falls back to direct Google Gemini API if OpenRouter free quotas are reached.

---

## 3. Review of User Stories Branch (`upstream/feat/issue-2-user-stories`)

*   **Assessment**: A remote branch was created containing three 0-byte placeholder files under `docs/user-stories/` for Campus Events, Degree Planning, and Lost & Found.
*   **Action Taken**: We drafted and finalized detailed user stories with concrete role definitions (Students, Advisors, Student Aids) and specific Acceptance Criteria for response latency, citation links, and source accuracy. These are now saved in:
    *   `docs/user-stories/DEGREE_PLANNING_STORIES.md`
    *   `docs/user-stories/CAMPUS_EVENTS_STORIES.md`
    *   `docs/user-stories/LOST_AND_FOUND_STORIES.md`

---

## 4. Current Stack Consensus Summary

```text
               [ Prototyping Stage ]
  Streamlit Web UI + ChromaDB (Local Vector Store)
                       │
                       ▼
               [ Production Stage ]
    React Frontend + Node.js Serverless Backend
                       │
                       ├─► Vector Queries: Neon Postgres (pgvector)
                       └─► LLM API: OpenRouter (Gemini / Gemma / Qwen)
```
*   **Agent Harness Evaluation**: Currently determining whether to use **Aider**, **AgentZero**, or **OpenCode** for automating coding tasks.
