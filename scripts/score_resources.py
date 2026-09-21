#!/usr/bin/env python3
"""Rank already-assessed resources; never fetches or verifies their sources.

Input: a non-empty resource list, or an object with resources and optional weights.
Every resource needs a name and six 0-5 scores. A partial weight mapping replaces
those defaults before normalization. Scoring does not enforce access/evidence
constraints; the agent must apply hard gates first. Python 3.10+, no dependencies.
"""
from __future__ import annotations

import argparse
import html
import math
import sys
from pathlib import Path
from typing import Any

if __package__:
    from ._common import DataError, array, dump_json, load_json, mapping, number, text
else:
    from _common import DataError, array, dump_json, load_json, mapping, number, text

DEFAULT_WEIGHTS = {
    "authority": 0.20,
    "relevance": 0.25,
    "practicality": 0.20,
    "currency": 0.15,
    "learner_fit": 0.15,
    "accessibility": 0.05,
}


def normalize(payload: Any) -> tuple[list[dict], dict[str, float]]:
    if isinstance(payload, list):
        resources = payload
        custom: dict = {}
    else:
        obj = mapping(payload, "top-level JSON")
        resources = obj.get("resources")
        custom = mapping(obj.get("weights", {}), "weights")
    array(resources, "resources", nonempty=True)
    unknown = set(custom) - set(DEFAULT_WEIGHTS)
    if unknown:
        raise DataError(f"unknown weight keys: {', '.join(sorted(map(str, unknown)))}")
    weights = DEFAULT_WEIGHTS.copy()
    for key, value in custom.items():
        weights[key] = number(value, f"weight '{key}'")
    scale = max(weights.values())
    if scale <= 0:
        raise DataError("sum of weights must be greater than zero")
    # Scale first so even multiple large but finite weights cannot overflow.
    scaled = {key: value / scale for key, value in weights.items()}
    total = math.fsum(scaled.values())
    return resources, {key: value / total for key, value in scaled.items()}


def _raw_score(resource: Any, weights: dict[str, float]) -> float:
    obj = mapping(resource, "resource")
    name = text(obj.get("name"), "resource name")
    scores = mapping(obj.get("scores"), f"resource '{name}' scores")
    unknown = set(scores) - set(DEFAULT_WEIGHTS)
    if unknown:
        raise DataError(f"resource '{name}' has unknown score keys: {sorted(unknown)}")
    values = {key: number(scores.get(key), f"resource '{name}' score '{key}'", 0, 5)
              for key in DEFAULT_WEIGHTS}
    return 20 * math.fsum(weights[key] * values[key] for key in DEFAULT_WEIGHTS)


def score_resource(resource: Any, weights: dict[str, float]) -> dict:
    # Public convenience function; callers should get weights from normalize().
    raw = _raw_score(resource, weights)
    return {**resource, "total_score": round(raw, 1)}


def rank_resources(payload: Any) -> dict:
    resources, weights = normalize(payload)
    assessed = [(_raw_score(item, weights), item) for item in resources]
    assessed.sort(key=lambda pair: pair[0], reverse=True)  # Stable, unrounded.
    # Keep schema/fixture/evidence metadata when ranking a full resource ledger.
    # A caller may save this result without silently losing its provenance flags.
    result = dict(payload) if isinstance(payload, dict) else {}
    result.update({
        "weights": weights,
        "resources": [{**item, "total_score": round(raw, 1)} for raw, item in assessed],
    })
    return result


def _cell(value: Any) -> str:
    escaped = html.escape(str(value), quote=False).replace("\\", "\\\\").replace("|", "\\|")
    return escaped.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def render_markdown(ranked: list[dict]) -> str:
    lines = ["| Rank | Resource | Type | Role | Score |", "|---:|---|---|---|---:|"]
    for index, item in enumerate(ranked, 1):
        lines.append(f"| {index} | {_cell(item['name'])} | {_cell(item.get('type', ''))} | "
                     f"{_cell(item.get('role', ''))} | {item['total_score']:.1f} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emit portable JSON rather than a Markdown table")
    args = parser.parse_args(argv)
    try:
        result = rank_resources(load_json(args.json_file))
        print(dump_json(result) if args.as_json else render_markdown(result["resources"]))
        return 0
    except (DataError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
