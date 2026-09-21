# Testing scope

## Local automated tests

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_repo.py .
python -m unittest discover -s tests -v
python -m unittest discover -s examples/python-testing/lab -v
```

The helper/unit tests cover strict JSON handling, finite numeric values, weight normalization, ranking precision, Markdown escaping, command-line errors, evidence metadata, local path boundaries, prerequisite cycles/order, coverage, resource/section references, total hours, schemas, and repository packaging. The example lab is separately tested.

The repository validator parses actual YAML with a safe duplicate-key-rejecting loader, validates the resource/plan/progress examples against bundled JSON Schemas, checks key progress invariants, and checks relative Markdown **file paths** (not headings/anchors, remote links, or a full Markdown syntax tree). It intentionally skips code-fenced examples and ignored output directories. The installed folder name must match `name`; for a GitHub archive checkout with a generated suffix, use `--allow-directory-name-mismatch` for source auditing only. Do not use that option as an installation fix.

Scoring and plan validation require only Python's standard library. Repository/schema checks also need PyYAML and jsonschema. No unit test requires internet, model credentials, or a paid API.

## CI

`.github/workflows/validate.yml` runs the checks on the specified Linux/Windows Python matrix. Permissions are read-only; it does not publish or use personal secrets. Hosted CI status must be observed on GitHub after pushing; a local test result is not a hosted workflow result.

## Behavioral evaluation is separate

Use `evals/prompts.json` with an installed skill and the intended host/model. Record host version, model, available tools, invocation, and actual outputs. Evaluate against `evals/rubric.md`, including offline and malicious-source cases. These cases are a **manual suite**, not automatically executed model tests.

A passing unit suite demonstrates deterministic helper behavior, not high-quality teaching, correct resource judgments, stable implicit triggering, or faster learning. No quantitative learning-effectiveness or universal compatibility claim is made. The publication audit distinguishes actual local checks from unperformed tests.
