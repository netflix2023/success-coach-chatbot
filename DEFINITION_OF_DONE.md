# Definition of Done (DoD)

This document outlines the standard quality requirements that all code submissions to the Success Coach Chatbot repository must satisfy before they can be merged into `main`.

---

## 1. Quality Gates & Checklist

A task is considered **Done** only when it meets the following criteria:

### 💻 Code Quality & Compilation
- [ ] **Compilation**: Code compiles and builds locally without errors.
- [ ] **Type-Checking**: No TypeScript errors (run `npx tsc --noEmit` in `apps/frontend`).
- [ ] **Linting & Formatting**: 
  - Next.js: ESLint checks pass (`npm run lint`).
  - Python: Ruff check passes (`uv run ruff check .`).
- [ ] **No Dead Code**: Remove all debug console logs (`console.log`), unused imports, and temporary commented-out code blocks.

### 🧪 Automated Testing
- [ ] **Unit Tests**: All existing and newly written unit tests pass.
  - Python tests run successfully (`uv run pytest` in `apps/data`).
  - Next.js tests run successfully (if applicable).
- [ ] **Regression Check**: The build workflow passes successfully inside GitHub Actions.

### 🔍 Verification & Local Testing
- [ ] **Local Execution**: The feature has been verified manually in a local development environment.
- [ ] **Cross-Browser/Responsive UI**: For frontend modifications, the UI must be tested for responsiveness (mobile, tablet, desktop) and verified on Chrome/Safari.

### 📝 Documentation
- [ ] **Inline Documentation**: Complicated logic is clearly explained with comments.
- [ ] **Public Documentation**: Update `README.md`, `techstack.md`, or architecture blueprints if introducing new dependencies, database schemas, or infrastructure.
- [ ] **Environment Variables**: Add new configuration parameters to `.env.example` (never commit active credentials).

### 👥 Code Review & Merging
- [ ] **Pull Request**: A PR is opened using the standard [Pull Request Template](.github/pull_request_template.md).
- [ ] **Peer Review**: At least **one approving review** is secured from a repository administrator/maintainer.
- [ ] **CI Pipeline**: The CI workflow runs green on the pull request.

---

## 2. Python (uv) Specific DoD
*   Add any new dependencies via `uv add <package>` to ensure `pyproject.toml` and `uv.lock` are lock-synchronized.
*   Ensure all data extraction pipelines log structural metrics (e.g. number of scraped records, failed parses).

## 3. Next.js / Frontend Specific DoD
*   Verify that API response parsing handles edge cases (e.g., empty source lists, network timeout fallbacks).
*   Avoid inline styling; utilize standard Tailwind classes and keep components modular.
