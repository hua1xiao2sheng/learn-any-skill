# Contributing

Keep changes focused on turning a learning goal into an evidence-grounded, teachable course. Do not add a framework, crawler, paid API, automatic scheduler, or tool permission dependency merely to make the skill appear more capable.

For local checks:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py .
python -m unittest discover -s tests -v
python -m unittest discover -s examples/python-testing/lab -v
```

Include regression tests for script bugs, update relevant schemas/examples/docs together, and add a changelog entry for user-visible changes. Keep the root `SKILL.md` concise and use focused references for detail. Name the installed folder `learn-any-skill`.

Behavior changes need manual evaluation using `evals/prompts.json` and `evals/rubric.md`. Record model/host/tool configuration and results instead of claiming universal improvements. Do not submit personal learner logs or copyrighted course content. Please write issues and documentation in English or Chinese; both are welcome.
