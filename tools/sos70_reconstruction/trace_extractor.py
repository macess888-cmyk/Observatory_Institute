from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class TraceRecoverability(Enum):
    OBSERVED = "OBSERVED"
    MISSING = "MISSING"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True)
class TraceColumnResult:
    pixel_x: int
    pixel_y: float | None
    pixel_y_lower: int | None
    pixel_y_upper: int | None
    candidate_count: int
    recoverability: TraceRecoverability


def _validate_mask(mask: Sequence[Sequence[bool]]) -> tuple[int, int]:
    if not mask:
        raise ValueError("mask must contain at least one row")

    width = len(mask[0])

    if width == 0:
        raise ValueError("mask must contain at least one column")

    for row in mask:
        if len(row) != width:
            raise ValueError("mask must be rectangular")

        for value in row:
            if type(value) is not bool:
                raise TypeError("mask values must be bool")

    return len(mask), width


def _contiguous_groups(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []

    groups: list[list[int]] = [[indices[0]]]

    for index in indices[1:]:
        if index == groups[-1][-1] + 1:
            groups[-1].append(index)
        else:
            groups.append([index])

    return groups


def extract_trace_from_mask(
    mask: Sequence[Sequence[bool]],
) -> tuple[TraceColumnResult, ...]:
    height, width = _validate_mask(mask)

    results: list[TraceColumnResult] = []

    for pixel_x in range(width):
        candidate_rows = [
            pixel_y
            for pixel_y in range(height)
            if mask[pixel_y][pixel_x]
        ]

        candidate_count = len(candidate_rows)

        if candidate_count == 0:
            results.append(
                TraceColumnResult(
                    pixel_x=pixel_x,
                    pixel_y=None,
                    pixel_y_lower=None,
                    pixel_y_upper=None,
                    candidate_count=0,
                    recoverability=TraceRecoverability.MISSING,
                )
            )
            continue

        groups = _contiguous_groups(candidate_rows)

        if len(groups) != 1:
            results.append(
                TraceColumnResult(
                    pixel_x=pixel_x,
                    pixel_y=None,
                    pixel_y_lower=candidate_rows[0],
                    pixel_y_upper=candidate_rows[-1],
                    candidate_count=candidate_count,
                    recoverability=TraceRecoverability.AMBIGUOUS,
                )
            )
            continue

        segment = groups[0]
        lower = segment[0]
        upper = segment[-1]
        centre = (lower + upper) / 2.0

        results.append(
            TraceColumnResult(
                pixel_x=pixel_x,
                pixel_y=centre,
                pixel_y_lower=lower,
                pixel_y_upper=upper,
                candidate_count=candidate_count,
                recoverability=TraceRecoverability.OBSERVED,
            )
        )

    return tuple(results)