# Changelog

## 0.2.0 — 2026-09-21

### Added
- Plan/build/teach/review/resume/refresh behavior, original lesson-card guidance, and explicit learner-evidence gates.
- Source-verification states, gap-directed bounded search, capability coverage, and offline/tool fallbacks.
- Structured plan/resource/progress schemas and reusable templates.
- A deterministic curriculum validator for prerequisites, coverage, evidence metadata, and time budget.
- A complete small Python testing course with an executable practice lab.
- Unit tests, repository/schema validation, behavioral evaluation prompts, bilingual documentation, and a Windows/GitHub publishing guide.
- Privacy, prompt-injection, permission, and copyright boundaries.

### Fixed
- Boolean scores/weights, non-finite numbers, malformed weight containers, duplicate JSON keys, empty inputs, Unicode/IO errors, and unsafe Markdown cell rendering in the scoring helper.
- Rounded-score sorting: rank on unrounded totals, round only for display.
- User-level Codex installation examples now follow `$HOME/.agents/skills` in the official documentation checked on 2026-09-21.

### Clarified
- The skill is host-driven instructions plus local helpers, not a self-running search engine or scheduler.
- Numerical rankings are subjective decision aids; validators cannot certify source truth or pedagogical quality.
- GitHub publication is not plugin-directory registration; no remote publishing is performed by this repository.

## 0.1.0

Initial source-curation and project-first roadmap instructions, rubric, scoring helper, and basic CI smoke check.
