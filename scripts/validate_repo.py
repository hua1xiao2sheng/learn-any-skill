#!/usr/bin/env python3
"""Validate this repository's packaging, local links, YAML and JSON examples.

Requires requirements-dev.txt. Does not contact remote URLs or run a model.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

if __package__:
    from ._common import DataError, load_json
    from .validate_plan import validate_plan
else:
    from _common import DataError, load_json
    from validate_plan import validate_plan

IGNORED = {".git", ".learning", ".venv", "venv", "__pycache__", ".pytest_cache", "dist"}
REQUIRED = [
    "SKILL.md", "README.md", "README.zh-CN.md", "LICENSE", "VERSION", "CHANGELOG.md",
    "SECURITY.md", "CONTRIBUTING.md", "agents/openai.yaml", ".github/workflows/validate.yml",
    "scripts/score_resources.py", "scripts/validate_plan.py", "scripts/validate_repo.py",
    "schemas/resources.schema.json", "schemas/plan.schema.json", "schemas/progress.schema.json",
    "templates/lesson.md", "templates/progress.json", "evals/prompts.json", "evals/rubric.md",
    "docs/INSTALLATION.md", "docs/PUBLISH.zh-CN.md", "docs/AUDIT.zh-CN.md", "docs/TESTING.md",
]


def parse_yaml(raw: str, label: str):
    try:
        import yaml
    except ImportError as exc:
        raise DataError("install development dependencies: python -m pip install -r requirements-dev.txt") from exc

    class UniqueSafeLoader(yaml.SafeLoader):
        pass

    def unique_mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            try:
                if key in result:
                    raise DataError(f"{label}: duplicate YAML key {key!r}")
                result[key] = loader.construct_object(value_node, deep=deep)
            except TypeError as exc:
                raise DataError(f"{label}: unsupported YAML mapping key") from exc
        return result

    UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
    try:
        return yaml.load(raw, Loader=UniqueSafeLoader)
    except yaml.YAMLError as exc:
        raise DataError(f"{label}: invalid YAML: {exc}") from exc


def validate_frontmatter(raw: str, directory_name: str, allow_name_mismatch: bool = False) -> dict:
    lines = raw.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        raise DataError("SKILL.md must start with YAML frontmatter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise DataError("SKILL.md frontmatter has no closing ---") from exc
    front = parse_yaml("\n".join(lines[1:end]), "SKILL.md")
    if not isinstance(front, dict):
        raise DataError("SKILL.md frontmatter must be a mapping")
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    if set(front) - allowed:
        raise DataError(f"unknown SKILL.md frontmatter keys: {set(front) - allowed}")
    name = front.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise DataError("invalid skill name: use 1-64 lowercase letters/digits/hyphens, no --")
    if name != directory_name and not allow_name_mismatch:
        raise DataError(f"skill name {name!r} does not match directory {directory_name!r}")
    desc = front.get("description")
    if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
        raise DataError("description must be a non-empty string of at most 1024 characters")
    if "compatibility" in front:
        value = front["compatibility"]
        if not isinstance(value, str) or not 1 <= len(value) <= 500:
            raise DataError("compatibility must contain 1-500 characters")
    if "metadata" in front:
        meta = front["metadata"]
        if not isinstance(meta, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in meta.items()):
            raise DataError("metadata must map strings to strings")
    if not "\n".join(lines[end+1:]).strip():
        raise DataError("SKILL.md must contain a Markdown body")
    if len(lines) > 500:
        raise DataError("repository policy: keep SKILL.md at most 500 lines")
    return front


def markdown_links_exist(path: Path, root: Path) -> None:
    """Check relative inline Markdown file links, excluding fenced code/anchors."""
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"(?ms)^\x60\x60\x60.*?^\x60\x60\x60[^\n]*", "", raw)
    raw = re.sub(r"(?ms)^~~~.*?^~~~[^\n]*", "", raw)
    for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", raw):
        if target.startswith("#") or urlsplit(target).scheme:
            continue
        clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not clean:
            continue
        actual = (path.parent / clean).resolve()
        if not actual.is_relative_to(root.resolve()) or not actual.exists():
            raise DataError(f"{path.relative_to(root)}: broken/escaping local link {target}")


def validate_progress(progress: dict, plan: dict) -> None:
    lesson_ids = {lesson["id"] for lesson in plan["lessons"]}
    current = progress["current_lesson_id"]
    if current is not None and current not in lesson_ids:
        raise DataError("progress current_lesson_id is not in plan")
    seen = set()
    for state in progress["lesson_status"]:
        lid = state["lesson_id"]
        if lid in seen or lid not in lesson_ids:
            raise DataError(f"progress has duplicate or unknown lesson: {lid}")
        seen.add(lid)
        if state["status"] == "passed" and (not state["evidence"] or state["assistance"] == "not_assessed"):
            raise DataError(f"progress marks {lid} passed without assessment evidence")


def validate_repo(root: Path, allow_name_mismatch: bool = False) -> dict:
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as exc:
        raise DataError("install development dependencies: python -m pip install -r requirements-dev.txt") from exc
    root = root.resolve()
    if not root.is_dir():
        raise DataError(f"not a repository directory: {root}")
    for relative in REQUIRED:
        if not (root / relative).is_file():
            raise DataError(f"missing required file: {relative}")
    front = validate_frontmatter((root / "SKILL.md").read_text(encoding="utf-8"), root.name, allow_name_mismatch)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if front.get("metadata", {}).get("version") != version:
        raise DataError("VERSION and SKILL.md metadata.version differ")
    metadata = parse_yaml((root / "agents/openai.yaml").read_text(encoding="utf-8"), "agents/openai.yaml")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("interface"), dict):
        raise DataError("agents/openai.yaml needs an interface mapping")
    for field in ("display_name", "short_description", "default_prompt"):
        value = metadata["interface"].get(field)
        if not isinstance(value, str) or not value.strip():
            raise DataError(f"agents/openai.yaml: missing string {field}")
    if f"$" + front["name"] not in metadata["interface"]["default_prompt"]:
        raise DataError("default_prompt must reference the skill's actual name")
    if not isinstance(metadata.get("policy", {}).get("allow_implicit_invocation"), bool):
        raise DataError("invocation policy must be an explicit boolean")
    all_files = [p for p in root.rglob("*") if p.is_file() and not (set(p.relative_to(root).parts) & IGNORED)]
    for path in all_files:
        if path.suffix == ".md":
            markdown_links_exist(path, root)
        elif path.suffix in {".yml", ".yaml"}:
            parse_yaml(path.read_text(encoding="utf-8"), str(path.relative_to(root)))
        elif path.suffix == ".json":
            load_json(path)
        elif path.suffix == ".py":
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as exc:
                raise DataError(f"Python syntax error in {path}: {exc}") from exc
    validators = {}
    for kind in ("resources", "plan", "progress"):
        schema = load_json(root / f"schemas/{kind}.schema.json")
        Draft202012Validator.check_schema(schema)
        validators[kind] = Draft202012Validator(schema, format_checker=FormatChecker())
    cases = [
        ("resources", root / "examples/resources.example.json"),
        ("progress", root / "templates/progress.json"),
    ]
    for kind in validators:
        cases.append((kind, root / f"examples/python-testing/{kind}.json"))
    for kind, path in cases:
        error = next(validators[kind].iter_errors(load_json(path)), None)
        if error is not None:
            raise DataError(f"schema error in {path.relative_to(root)} at {list(error.path)}: {error.message}")
    sample = root / "examples/python-testing"
    plan = load_json(sample / "plan.json")
    summary = validate_plan(plan, load_json(sample / "resources.json"), sample)
    validate_progress(load_json(sample / "progress.json"), plan)
    return {"valid": True, "version": version, "files_checked": len(all_files),
            "schema_examples_checked": len(cases), "example_plan": summary}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--allow-directory-name-mismatch", action="store_true",
                        help="source-archive audit only; installations should match the skill name")
    args = parser.parse_args(argv)
    try:
        result = validate_repo(args.root, args.allow_directory_name_mismatch)
        print(f"PASS: repository v{result['version']}; {result['files_checked']} files inspected; "
              f"{result['schema_examples_checked']} schema examples validated.")
        print("Local checks only: not a live host evaluation, hosted CI result, or web-source check.")
        return 0
    except (DataError, OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
