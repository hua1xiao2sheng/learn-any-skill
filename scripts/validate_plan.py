#!/usr/bin/env python3
"""Offline curriculum consistency checks; this does not verify source truth.

Checks capability dependencies, selected resources/sections, declared evidence,
local file boundaries, lesson order, required coverage, and time budget. Inputs
are plan.json plus a resource ledger. Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from collections import deque
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

if __package__:
    from ._common import DataError, array, dump_json, load_json, mapping, number, strings, text
else:
    from _common import DataError, array, dump_json, load_json, mapping, number, strings, text

ID_PATTERN = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*\Z")
VERIFICATION_STATUSES = {"content-verified", "metadata-only", "unverified", "local"}
KINDS = {"guided", "independent", "transfer", "review"}


def identifier(value: Any, label: str) -> str:
    result = text(value, label)
    if value != result or not ID_PATTERN.fullmatch(result):
        raise DataError(f"{label} must be a lowercase ID using letters, digits, hyphens or underscores")
    return result


def _keys(obj: dict, allowed: set[str], label: str) -> None:
    unknown = set(obj) - allowed
    if unknown:
        raise DataError(f"{label} contains unknown fields: {sorted(map(str, unknown))}")


def _checked_date(value: Any, label: str) -> None:
    raw = text(value, label)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise DataError(f"{label} must be an ISO date YYYY-MM-DD")
    try:
        observed = date.fromisoformat(raw)
    except ValueError as exc:
        raise DataError(f"{label} is not a calendar date") from exc
    if observed > date.today():
        raise DataError(f"{label} cannot be in the future")


def _locator(value: Any, label: str, base_dir: Path | None) -> str:
    raw = text(value, label)
    if raw.startswith("repo:"):
        relative = raw[5:]
        if not relative or relative.startswith(("/", "\")) or "\" in relative or ":" in relative:
            raise DataError(f"{label}: repo locator must be a relative POSIX-style path")
        path = Path(relative)
        if ".." in path.parts:
            raise DataError(f"{label}: local path traversal is not allowed")
        if base_dir is not None:
            root = base_dir.resolve()
            resolved = (root / path).resolve()
            if not resolved.is_relative_to(root):
                raise DataError(f"{label}: local locator escapes the resource directory")
            if not resolved.is_file():
                raise DataError(f"{label}: local resource file not found: {relative}")
        return raw
    try:
        parts = urlsplit(raw)
        if parts.scheme not in {"https", "http"} or not parts.hostname:
            raise ValueError("missing HTTP(S) host")
        if parts.username is not None or parts.password is not None:
            raise ValueError("credentials are not allowed")
        if any(char.isspace() for char in raw):
            raise ValueError("whitespace is not allowed")
        _ = parts.port
    except ValueError as exc:
        raise DataError(f"{label}: expected an HTTP(S) URL without credentials, or repo:relative/path") from exc
    return raw


def _resources(ledger: Any, base_dir: Path | None) -> dict[str, dict]:
    obj = mapping(ledger, "resource ledger")
    if obj.get("schema_version") != "0.2":
        raise DataError("resource ledger schema_version must be '0.2'")
    result: dict[str, dict] = {}
    for item in array(obj.get("resources"), "resources", nonempty=True):
        resource = mapping(item, "resource")
        rid = identifier(resource.get("id"), "resource id")
        if rid in result:
            raise DataError(f"duplicate resource id: {rid}")
        text(resource.get("name"), f"{rid}.name")
        if resource.get("type") not in {"docs", "course", "paper", "github", "video", "blog", "local"}:
            raise DataError(f"{rid}.type is invalid")
        if resource.get("role") not in {"core", "practice", "optional", "skip"}:
            raise DataError(f"{rid}.role is invalid")
        if resource.get("access") not in {"free", "paid", "mixed", "unknown", "local"}:
            raise DataError(f"{rid}.access is invalid")
        url = _locator(resource.get("url"), f"{rid}.url", base_dir)
        strings(resource.get("covers"), f"{rid}.covers")
        verification = mapping(resource.get("verification"), f"{rid}.verification")
        status = verification.get("status")
        if status not in VERIFICATION_STATUSES:
            raise DataError(f"{rid}: unknown verification status")
        if status != "unverified":
            _checked_date(verification.get("checked_at"), f"{rid}.checked_at")
            text(verification.get("evidence"), f"{rid}.evidence")
        elif verification.get("checked_at") is not None:
            _checked_date(verification["checked_at"], f"{rid}.checked_at")
        if status == "local" and not url.startswith("repo:"):
            raise DataError(f"{rid}: local verification requires a repo: locator")
        if url.startswith("repo:") and status != "local":
            raise DataError(f"{rid}: repo: resources must use local verification")
        if verification.get("evidence_url"):
            _locator(verification["evidence_url"], f"{rid}.evidence_url", base_dir)
        section_ids: set[str] = set()
        for raw_section in array(resource.get("sections"), f"{rid}.sections"):
            section = mapping(raw_section, f"{rid} section")
            sid = identifier(section.get("id"), "section id")
            if sid in section_ids:
                raise DataError(f"{rid}: duplicate section id {sid}")
            section_ids.add(sid)
            text(section.get("title"), f"{rid}/{sid}.title")
            _locator(section.get("locator"), f"{rid}/{sid}.locator", base_dir)
            if not isinstance(section.get("verified"), bool):
                raise DataError(f"{rid}/{sid}.verified must be a boolean")
        result[rid] = resource
    return result


def validate_plan(plan: Any, ledger: Any, base_dir: Path | None = None) -> dict:
    obj = mapping(plan, "plan")
    _keys(obj, {"schema_version", "skill", "mode", "language", "budget_hours", "buffer_hours",
                "max_core_resources", "capabilities", "known_capabilities",
                "selected_resource_ids", "lessons", "notes"}, "plan")
    if obj.get("schema_version") != "0.2":
        raise DataError("plan schema_version must be '0.2'")
    text(obj.get("skill"), "skill")
    text(obj.get("language"), "language")
    mode = obj.get("mode")
    if mode not in {"verified", "offline"}:
        raise DataError("plan mode must be 'verified' or 'offline'")
    budget = number(obj.get("budget_hours"), "budget_hours")
    if budget <= 0:
        raise DataError("budget_hours must be positive")
    buffer = number(obj.get("buffer_hours"), "buffer_hours")
    cap_map: dict[str, dict] = {}
    for item in array(obj.get("capabilities"), "capabilities", nonempty=True):
        cap = mapping(item, "capability")
        _keys(cap, {"id", "title", "requires", "required"}, "capability")
        cid = identifier(cap.get("id"), "capability id")
        if cid in cap_map:
            raise DataError(f"duplicate capability id: {cid}")
        text(cap.get("title"), f"{cid}.title")
        strings(cap.get("requires"), f"{cid}.requires")
        if not isinstance(cap.get("required"), bool):
            raise DataError(f"{cid}.required must be a boolean")
        cap_map[cid] = cap
    indegree = {cid: len(cap["requires"]) for cid, cap in cap_map.items()}
    children: dict[str, list[str]] = {cid: [] for cid in cap_map}
    for cid, cap in cap_map.items():
        for dependency in cap["requires"]:
            if dependency not in cap_map:
                raise DataError(f"{cid}: unknown prerequisite {dependency}")
            children[dependency].append(cid)
    queue = deque(cid for cid, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        current = queue.popleft()
        visited += 1
        for child in children[current]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(cap_map):
        raise DataError("capability prerequisite graph contains a cycle")

    known = set(strings(obj.get("known_capabilities"), "known_capabilities"))
    if not known <= cap_map.keys():
        raise DataError(f"unknown known_capabilities: {sorted(known - cap_map.keys())}")
    resource_map = _resources(ledger, base_dir)
    selected_list = strings(obj.get("selected_resource_ids"), "selected_resource_ids", nonempty=True)
    selected = set(selected_list)
    if not selected <= resource_map.keys():
        raise DataError(f"unknown selected resources: {sorted(selected - resource_map.keys())}")
    warnings: list[str] = []
    if base_dir is None and any(r["url"].startswith("repo:") for r in resource_map.values()):
        warnings.append("Local paths were syntax-checked only; pass base_dir to check file existence.")
    if mode == "offline":
        warnings.append("Offline/provisional plan: source truth and current availability are not certified.")
    for rid in selected:
        r = resource_map[rid]
        if r["role"] == "skip":
            raise DataError(f"selected resource {rid} is marked skip")
        unknown_coverage = set(r["covers"]) - cap_map.keys()
        if unknown_coverage:
            raise DataError(f"{rid}: unknown covered capabilities {sorted(unknown_coverage)}")
        if mode == "verified" and r["verification"]["status"] not in {"content-verified", "local"}:
            raise DataError(f"verified plan selects unverified/metadata-only resource: {rid}")
        if mode == "offline" and r["verification"]["status"] in {"metadata-only", "unverified"}:
            warnings.append(f"Provisional selected resource: {rid}")
    maximum = obj.get("max_core_resources")
    if maximum is not None:
        if isinstance(maximum, bool) or not isinstance(maximum, int) or maximum <= 0:
            raise DataError("max_core_resources must be a positive integer")
        core_count = sum(resource_map[r]["role"] == "core" for r in selected)
        if core_count > maximum:
            raise DataError(f"selected {core_count} core resources exceeds max_core_resources={maximum}")

    acquired = set(known)
    used_resources: set[str] = set()
    lesson_ids: set[str] = set()
    totals = {"input": 0.0, "practice": 0.0, "assessment": 0.0}
    elapsed = 0.0
    first_practice: float | None = None
    independent = False
    for raw_lesson in array(obj.get("lessons"), "lessons", nonempty=True):
        lesson = mapping(raw_lesson, "lesson")
        _keys(lesson, {"id", "title", "kind", "capabilities", "resource_ids", "section_refs",
                       "hours", "exercise", "output", "exit_criteria"}, "lesson")
        lid = identifier(lesson.get("id"), "lesson id")
        if lid in lesson_ids:
            raise DataError(f"duplicate lesson id: {lid}")
        lesson_ids.add(lid)
        text(lesson.get("title"), f"{lid}.title")
        for field in ("exercise", "output"):
            text(lesson.get(field), f"{lid}.{field}")
        strings(lesson.get("exit_criteria"), f"{lid}.exit_criteria", nonempty=True)
        kind = lesson.get("kind")
        if kind not in KINDS:
            raise DataError(f"{lid}: unknown lesson kind")
        independent |= kind in {"independent", "transfer"}
        caps = strings(lesson.get("capabilities"), f"{lid}.capabilities", nonempty=True)
        if not set(caps) <= cap_map.keys():
            raise DataError(f"{lid}: lesson contains unknown capability")
        refs = set(strings(lesson.get("resource_ids"), f"{lid}.resource_ids"))
        if not refs <= selected:
            raise DataError(f"{lid}: references unselected/unknown resources {sorted(refs - selected)}")
        used_resources |= refs
        seen_sections: set[tuple[str, str]] = set()
        for raw_ref in array(lesson.get("section_refs"), f"{lid}.section_refs"):
            ref = mapping(raw_ref, f"{lid} section reference")
            _keys(ref, {"resource_id", "section_id"}, "section reference")
            rid = text(ref.get("resource_id"), "section resource_id")
            sid = text(ref.get("section_id"), "section_id")
            if rid not in refs:
                raise DataError(f"{lid}: section resource {rid} is not in the lesson's resource_ids")
            if (rid, sid) in seen_sections:
                raise DataError(f"{lid}: duplicate section reference {rid}/{sid}")
            seen_sections.add((rid, sid))
            sections = {s["id"]: s for s in resource_map[rid]["sections"]}
            if sid not in sections:
                raise DataError(f"{lid}: unknown section {rid}/{sid}")
            if mode == "verified" and not sections[sid]["verified"]:
                raise DataError(f"{lid}: unverified section {rid}/{sid}")
        for cid in caps:
            if cid in acquired:
                continue
            missing = set(cap_map[cid]["requires"]) - acquired
            if missing:
                raise DataError(f"{lid}/{cid}: prerequisite not learned yet: {sorted(missing)}")
            if not any(cid in resource_map[rid]["covers"] for rid in refs):
                raise DataError(f"{lid}/{cid}: no referenced resource declares capability coverage")
            acquired.add(cid)
        hours = mapping(lesson.get("hours"), f"{lid}.hours")
        _keys(hours, set(totals), f"{lid}.hours")
        lesson_hours = {field: number(hours.get(field), f"{lid}.hours.{field}") for field in totals}
        lesson_total = math.fsum(lesson_hours.values())
        if lesson_total <= 0:
            raise DataError(f"{lid}: scheduled lesson must have positive total hours")
        if first_practice is None and lesson_hours["practice"] > 0:
            first_practice = elapsed + lesson_hours["input"]
        elapsed += lesson_total
        for field, value in lesson_hours.items():
            totals[field] += value
    required = {cid for cid, cap in cap_map.items() if cap["required"]}
    gaps = required - acquired
    if gaps:
        raise DataError(f"required capabilities are not covered: {sorted(gaps)}")
    if selected != used_resources:
        raise DataError(f"selected resources are unused: {sorted(selected - used_resources)}")
    total = elapsed + buffer
    if not math.isfinite(total) or total > budget + 1e-9:
        raise DataError(f"planned hours plus buffer ({total:g}) exceed budget ({budget:g})")
    if not independent:
        warnings.append("No independent/transfer lesson is scheduled; consider a mastery check.")
    if first_practice is None:
        warnings.append("No practice time is scheduled; check whether this fits the learning goal.")
    elif first_practice > 0.2 * elapsed + 1e-9:
        warnings.append("First practice starts after 20% of lesson time (design heuristic, not a hard rule).")
    return {
        "valid": True,
        "mode": mode,
        "lessons": len(lesson_ids),
        "required_capabilities": len(required),
        "covered_required_capabilities": len(required & acquired),
        "selected_resources": len(selected),
        "hours": {**{k: round(v, 6) for k, v in totals.items()}, "buffer": buffer,
                  "total": round(total, 6), "budget": budget},
        "warnings": warnings,
        "limitations": "Checks declared structure/evidence only; no live source or learning-effectiveness verification.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--resources", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        result = validate_plan(load_json(args.plan), load_json(args.resources), args.resources.parent)
        if args.as_json:
            print(dump_json(result))
        else:
            hours = result["hours"]
            print(f"PASS: {result['lessons']} lessons; "
                  f"{result['covered_required_capabilities']}/{result['required_capabilities']} required capabilities; "
                  f"{hours['total']:g}/{hours['budget']:g} hours (including buffer).")
            for warning in result["warnings"]:
                print(f"WARNING: {warning}")
            print(result["limitations"])
        return 0
    except (DataError, OSError, UnicodeError, OverflowError) as exc:
        if args.as_json:
            print(dump_json({"valid": False, "error": str(exc)}))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
