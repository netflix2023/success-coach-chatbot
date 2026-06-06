# Description

Please provide a summary of the change, including the problem being solved, the proposed architecture or implementation details, and any context that would be helpful to reviewers.

Fixes/Closes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update (no functional code changes)
- [ ] Refactoring / Code style improvements (formatting, linting)

# Checklist

Please verify that your Pull Request meets the following criteria before requesting review:

## 🛠️ Code Standards
- [ ] Code compiles and builds locally without errors.
- [ ] TypeScript compiler runs clean (`npx tsc --noEmit` in `apps/frontend`).
- [ ] Linting and formatting checks pass (`npm run lint` and `ruff check .`).
- [ ] Code follows the established project structure and styles (e.g., glassmorphic Tailwind UI).

## 🧪 Testing & Verification
- [ ] Existing and new unit tests run and pass (`uv run pytest` in `apps/data`).
- [ ] Feature has been verified manually in a local running environment.
- [ ] For UI changes: tested for mobile responsiveness and layout fidelity.

## 📝 Documentation & Configs
- [ ] Appropriate inline comments and docstrings have been added.
- [ ] Public documentation (README, techstack, infrastructure) has been updated if necessary.
- [ ] No active API keys or credentials have been committed. New variables are documented in `.env.example`.
