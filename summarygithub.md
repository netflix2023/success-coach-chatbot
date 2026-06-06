# GitHub Repository Summary

This file summarizes the current state of the club repository `Dallas-College-AI-Club/success-coach-chatbot` as of June 4, 2026.

---

## 1. Active Branches & Commits

### Branch: `main`
* **Status:** Stable base.
* **Contains:** Bare repository setup (`.gitignore`, `LICENSE`, `README.md`).

### Branch / PR #17: `initial_commit` (Author: @dbracewell)
* **Status:** Open Pull Request (Needs Review).
* **Summary:** Initial monorepo scaffolding for the project.
* **Tech Stack Scaffolded:**
  * **Frontend (`apps/frontend`):** Next.js 15, TypeScript, Tailwind CSS, Prettier, ESLint, and Shadcn UI.
  * **Data Engine (`apps/data`):** Python workspace managed by `uv` (a fast packaging tool), including unit tests (`pytest`), package configuration (`pyproject.toml`), and main python script structure.

---

## 2. Active Issue Assignments & Discussions

### Issue #10: Evaluate 3rd-Party Free Tier Services & Agnostic LLM Architecture
* **Status:** Completed (ADR created and approved)
* **Assignees:** `@darrian-xxv` and `@tjchan001`
* **Resolution Summary:**
  * Final decisions documented in [INFRASTRUCTURE_ARCHITECTURE.md](file:///mnt/chromeos/GoogleDrive/MyDrive/AntigravityProjects/SucesscoachChatbot/docs/INFRASTRUCTURE_ARCHITECTURE.md).
  * **Selected DB**: Neon Postgres (pgvector) for production and ChromaDB for local prototyping.
  * **Selected Host**: Vercel for React frontend and Node.js backend.
  * **Selected LLM Gateway**: OpenRouter with direct Gemini API key fallback.
  * **Rate Limiting**: Custom token-bucket edge rate limits to preserve the 15 RPM free Gemini tier limit.

### Issue #2: User Stories Definition
* **Status:** Completed (Stories written)
* **Assignees:** Project Team / Collaborators
* **Resolution Summary:**
  * Completed user stories and acceptance criteria for all placeholder categories inside the [docs/user-stories/](file:///mnt/chromeos/GoogleDrive/MyDrive/AntigravityProjects/SucesscoachChatbot/docs/user-stories/) directory:
    * [DEGREE_PLANNING_STORIES.md](file:///mnt/chromeos/GoogleDrive/MyDrive/AntigravityProjects/SucesscoachChatbot/docs/user-stories/DEGREE_PLANNING_STORIES.md)
    * [CAMPUS_EVENTS_STORIES.md](file:///mnt/chromeos/GoogleDrive/MyDrive/AntigravityProjects/SucesscoachChatbot/docs/user-stories/CAMPUS_EVENTS_STORIES.md)
    * [LOST_AND_FOUND_STORIES.md](file:///mnt/chromeos/GoogleDrive/MyDrive/AntigravityProjects/SucesscoachChatbot/docs/user-stories/LOST_AND_FOUND_STORIES.md)

---

## 3. Scaffold Files Added in PR #17

Below is the file tree introduced in the scaffold:

* **Top-Level:**
  * `.gitignore`
  * `README.md`
* **Data Layer (`apps/data/`):**
  * `.python-version` (Specifies python version)
  * `pyproject.toml` & `uv.lock` (Python packaging configurations)
  * `README.md`
  * `dallasai/`
    * `__init__.py`
    * `main.py` (Main Python entrypoint)
  * `tests/`
    * `__init__.py`
    * `test_main.py` (Sample pytests)
* **Frontend App (`apps/frontend/`):**
  * `package.json` & `package-lock.json`
  * `tsconfig.json`
  * `next.config.ts`
  * `postcss.config.mjs`
  * `eslint.config.mjs`
  * `.prettierrc`
  * `components.json` (Shadcn configurations)
  * `app/`
    * `layout.tsx` (Global page layout)
    * `page.tsx` (Next.js homepage template)
    * `globals.css` (Tailwind styles)
  * `components/ui/`
    * `button.tsx` (Shadcn button UI component)
  * `public/` (Vercel/Next SVGs)
  * `AGENTS.md` & `CLAUDE.md` (Agent instructions and run protocols)

---

## 4. Pull Request Review & Comments (PR #17)

* **Open Reviews:** 
  * Automated **GitHub Copilot Reviewer** has analyzed the PR.
  * Copilot generated **19 review comments** across 20 files. Key notes suggest standard React structure improvements and verified the config setups for `uv` and Next.js compiler targets.
* **Merge Requirements:** 
  * Needs at least **1 approving review** from a repository administrator before it can be merged into `main`.

---

## 5. How to Sync and See this Code Locally

If you want to pull this scaffold locally into your workspace to check out the folders, run:

```bash
# 1. Fetch all updates from the club's repository
git fetch upstream

# 2. Checkout the initial_commit branch as a local branch
git checkout -b initial_commit upstream/initial_commit
```

Once checked out, you will see the `apps/` directory and can work directly within the monorepo using Aider!
