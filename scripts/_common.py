"""Strict data loading and small validation primitives (standard library only)."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


class DataError(ValueError):
    """An invalid input that should be reported without a traceback by a CLI."""


def number(value: Any, label: str, minimum: float = 0.0,
           maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DataError(f"{label} must be a finite number (not a boolean)")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise DataError(f"{label} must be a finite number") from exc
    if not math.isfinite(result):
        raise DataError(f"{label} must be finite")
    if result < minimum or (maximum is not None and result > maximum):
        bound = f" in [{minimum}, {maximum}]" if maximum is not None else f" >= {minimum}"
        raise DataError(f"{label} must be{bound}")
    return result


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DataError(f"{label} must be a non-empty string")
    return value.strip()


def mapping(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise DataError(f"{label} must be an object")
    return value


def array(value: Any, label: str, nonempty: bool = False) -> list:
    if not isinstance(value, list) or (nonempty and not value):
        raise DataError(f"{label} must be a {'non-empty ' if nonempty else ''}list")
    return value


def strings(value: Any, label: str, nonempty: bool = False) -> list[str]:
    items = [text(item, label) for item in array(value, label, nonempty)]
    if len(items) != len(set(items)):
        raise DataError(f"{label} contains duplicate values")
    return items


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise DataError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise DataError(f"non-standard JSON numeric constant: {value}")


def _parse_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise DataError(f"JSON number is not finite: {value}")
    return result


def load_json(path: Path) -> Any:
    """Read UTF-8/BOM JSON, rejecting duplicate keys and non-finite literals."""
    try:
        raw = path.read_text(encoding="utf-8-sig")
        return json.loads(raw, object_pairs_hook=_object_pairs,
                          parse_constant=_reject_constant, parse_float=_parse_float)
    except DataError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise DataError(f"cannot read valid JSON from {path}: {exc}") from exc


def dump_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2)
