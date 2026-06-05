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
* **Status:** In progress (Success Coach Kanban Board)
* **Assignees:** `@darrian-xxv` and `@tjchan001`
* **Discussion Summary:**
  * **Constraints Check:** `@tjchan001` queried whether the stack is free-tier only or if there is a budget. `@dbracewell` clarified that since there is no club budget, the focus is on free tiers but ranking cheap, high-performance alternatives is highly encouraged.
  * **Architecture Proposal (by @tjchan001):** Proposed a hybrid Retrieval-Augmented Generation (RAG) architecture supporting over 800 courses and 300 degree programs. The recommendation selects Google's **Gemma 4 (31B)** as the primary model due to context size, with supplemental routing to **NVIDIA Nemotron 3 Super** and **Qwen3** variants via **OpenRouter** as the unified API layer.

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
