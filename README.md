# Learn Any Skill

**Turn a learning goal into a small, source-grounded course—not a list of links.**

[简体中文](README.zh-CN.md) · [Install](docs/INSTALLATION.md) · [Publish to GitHub](docs/PUBLISH.zh-CN.md) · [Audit](docs/AUDIT.zh-CN.md)

Version **0.2.0** · MIT · Optional helpers: Python 3.10+

## What it does

An agent uses this skill to clarify an observable goal, map prerequisites, inspect relevant courses/docs/papers/repos, remove overlap, and compose a project-first curriculum. It can then write original lesson cards, teach one lesson at a time, assess submitted work, and continue from a saved checkpoint.

```text
Goal + constraints → capability map → source inspection → minimal sufficient selection
                  → lessons + practice + gates → evidence-based progress → targeted review
```

The host provides the model, search/page-reading tools, shell, and filesystem. **This repository is not a standalone search service, automatic course downloader, LMS, or scheduler.** The local helpers are offline and do not call a model API. Their successful checks do not prove teaching effectiveness or web-source truth.

## Quick start in Codex

Copy this complete folder (not only `SKILL.md`) to one of the following:

```text
User-level:     ~/.agents/skills/learn-any-skill/
Project-level:  <your-project>/.agents/skills/learn-any-skill/
```

The installed folder should be named `learn-any-skill`. If a GitHub ZIP expands to `learn-any-skill-main`, rename it when installing. See [installation details, including Windows](docs/INSTALLATION.md).

Then send this **inside the agent's chat**, not in a shell:

```text
Use $learn-any-skill to plan a course on RAG.
I know Python and basic PyTorch. I have 14 hours in total.
Use free resources and no more than 3 core sources.
Prioritize retrieval evaluation, debugging, and an independent project.
Save the course under .learning/rag/.
```

Continue with:

```text
Use $learn-any-skill to build the lesson cards for .learning/rag/.
Use $learn-any-skill to teach lesson 1 without giving the exercise solution first.
Use $learn-any-skill to review my submitted exercise and update the checkpoint.
Use $learn-any-skill to resume .learning/rag/ from the saved progress.
```

`plan`, `build`, `teach`, `review`, `resume`, and `refresh` are intents interpreted by the skill, not registered slash commands. Live verification requires tools that can actually inspect sources. Without them, the output is explicitly provisional/offline.

## What the learner receives

A substantial course export contains a brief, source ledger, capability/lesson plan, readable curriculum, and progress checkpoint. Build mode also produces original lesson cards:

```text
.learning/rag/
├── brief.json
├── resources.json
├── plan.json
├── curriculum.md
├── progress.json
└── lessons/
    ├── 01-....md
    └── ...
```

Every lesson has a purpose, sources/sections, original explanation, practice, artifact, and mastery gate. Source runtime and estimated learning time are separate. A checkpoint is updated only from actual activity; explaining a lesson does not mark it passed.

## Try the bundled example without an API

The complete [Python testing mini-course](examples/python-testing/curriculum.zh-CN.md) uses two inspected official documentation pages and an original local lab. It demonstrates a 4-hour planning budget, not a promise of mastery. It is not a full RAG course.

From the repository root:

```bash
python scripts/score_resources.py examples/resources.example.json
python scripts/validate_plan.py examples/python-testing/plan.json --resources examples/python-testing/resources.json
python -m unittest discover -s examples/python-testing/lab -v
```

The scoring fixture is **synthetic**, explicitly marked unverified; its numbers are arithmetic test inputs, not course recommendations. The lab tests are reference solutions; run or inspect them for the release smoke check, but write your own tests before using them as a learner.

## What is deterministic—and what is not

| Component | Responsibility | Does not do |
|---|---|---|
| `SKILL.md` + references | Host-driven research, selection, teaching, feedback | Enforce a model's behavior deterministically |
| `score_resources.py` | Validate six supplied dimensions, normalize weights, rank | Search, judge courses objectively, enforce resource access |
| `validate_plan.py` | Check dependencies, declared evidence, references, coverage, time | Verify that a website really supports an assertion |
| `validate_repo.py` | Check packaging, YAML, local Markdown paths, JSON schemas/examples | Certify host compatibility or learning outcomes |
| `evals/` | Manual behavioral evaluation scenarios and rubric | Automatically grade live model runs |

Scores remain subjective. Resource selection is coverage-aware, not simply “take the top three.” Hard constraints are applied before scoring. No globally optimal shortest path or fixed speed-up is claimed.

## Repository layout

```text
learn-any-skill/
├── SKILL.md
├── README.md / README.zh-CN.md
├── agents/openai.yaml
├── references/              # Research, selection, teaching, output contracts
├── templates/               # Course, lesson, brief, checkpoint templates
├── schemas/                 # Resources, plan, progress JSON schemas
├── scripts/                 # Offline scoring and validation helpers
├── tests/                   # Automated regression tests
├── examples/python-testing/ # Complete small course and runnable lab
├── evals/                   # Manual agent behavior scenarios
├── docs/                    # Install, publish, audit, testing
├── .github/workflows/       # Read-only CI configuration
├── CONTRIBUTING.md / SECURITY.md / CHANGELOG.md
├── requirements-dev.txt
├── VERSION
└── LICENSE
```

## Developer checks

Only repository/schema validation needs the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py .
python -m unittest discover -s tests -v
python -m unittest discover -s examples/python-testing/lab -v
```

See [testing scope](docs/TESTING.md). Local test results are recorded in the audit; the GitHub-hosted matrix is configured but must actually run after publication. Cross-host behavior requires manual evaluation with the intended model and tool permissions.

## Privacy, licensing, and distribution

Keep personal output under `.learning/` outside the installed skill folder, and out of public commits. The helpers do not make network requests or collect telemetry. Read [SECURITY.md](SECURITY.md).

MIT covers this repository's original code/instructions, not linked third-party courses or content. Link and paraphrase; do not bypass paywalls or copy paid lessons. GitHub publishing makes the source available; it does not register a plugin in a product directory. Do not claim official endorsement or universal client compatibility.

## Format and installation references

Checked 2026-09-21: [OpenAI skill authoring/local discovery](https://learn.chatgpt.com/docs/build-skills) and [Agent Skills specification](https://agentskills.io/specification). The main entry follows the standard; `agents/openai.yaml` is host-specific optional metadata. Installation locations and tool capabilities can change; consult the host's current documentation.
