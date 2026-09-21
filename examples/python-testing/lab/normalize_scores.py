"""Small original teaching target. No network or third-party dependencies."""
from __future__ import annotations

import math
from collections.abc import Callable


def normalize_scores(values: list[int | float]) -> list[float]:
    """Map a non-empty list of finite numeric scores in [0, 100] to [0, 1].

    Booleans and non-numbers raise TypeError. Empty input, non-finite and
    out-of-range values raise ValueError. The input is not modified.
    """
    if not isinstance(values, list):
        raise TypeError("values must be a list")
    if not values:
        raise ValueError("values must not be empty")
    result = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("each score must be numeric and not boolean")
        # Compare integer bounds before float conversion, including enormous ints.
        if not 0 <= value <= 100 or not math.isfinite(value):
            raise ValueError("each score must be finite and in [0, 100]")
        result.append(value / 100)
    return result


def mean_from_loader(loader: Callable[[], list[int | float]]) -> float:
    """Call a supplied zero-argument loader once; normalize and return the mean.

    Loader exceptions propagate unchanged. Passing a function, rather than
    opening a network/file connection here, makes dependency isolation explicit.
    """
    normalized = normalize_scores(loader())
    return math.fsum(normalized) / len(normalized)
