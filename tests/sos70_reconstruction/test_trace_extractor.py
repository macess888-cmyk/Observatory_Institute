from __future__ import annotations

import pytest

from tools.sos70_reconstruction.trace_extractor import (
    TraceColumnResult,
    TraceRecoverability,
    extract_trace_from_mask,
)


def test_extracts_single_pixel_trace_per_column() -> None:
    mask = [
        [False, False, False, False],
        [True, False, False, False],
        [False, True, False, False],
        [False, False, True, False],
        [False, False, False, True],
    ]

    result = extract_trace_from_mask(mask)

    assert result == (
        TraceColumnResult(
            pixel_x=0,
            pixel_y=1.0,
            pixel_y_lower=1,
            pixel_y_upper=1,
            candidate_count=1,
            recoverability=TraceRecoverability.OBSERVED,
        ),
        TraceColumnResult(
            pixel_x=1,
            pixel_y=2.0,
            pixel_y_lower=2,
            pixel_y_upper=2,
            candidate_count=1,
            recoverability=TraceRecoverability.OBSERVED,
        ),
        TraceColumnResult(
            pixel_x=2,
            pixel_y=3.0,
            pixel_y_lower=3,
            pixel_y_upper=3,
            candidate_count=1,
            recoverability=TraceRecoverability.OBSERVED,
        ),
        TraceColumnResult(
            pixel_x=3,
            pixel_y=4.0,
            pixel_y_lower=4,
            pixel_y_upper=4,
            candidate_count=1,
            recoverability=TraceRecoverability.OBSERVED,
        ),
    )


def test_uses_centre_of_vertical_trace_thickness() -> None:
    mask = [
        [False],
        [True],
        [True],
        [True],
        [False],
    ]

    result = extract_trace_from_mask(mask)

    assert result[0].pixel_y == pytest.approx(2.0)
    assert result[0].pixel_y_lower == 1
    assert result[0].pixel_y_upper == 3
    assert result[0].candidate_count == 3
    assert result[0].recoverability is TraceRecoverability.OBSERVED


def test_marks_empty_column_as_missing() -> None:
    mask = [
        [False, False],
        [True, False],
        [False, False],
    ]

    result = extract_trace_from_mask(mask)

    assert result[0].recoverability is TraceRecoverability.OBSERVED
    assert result[1].recoverability is TraceRecoverability.MISSING
    assert result[1].pixel_y is None
    assert result[1].pixel_y_lower is None
    assert result[1].pixel_y_upper is None
    assert result[1].candidate_count == 0


def test_marks_disconnected_candidates_as_ambiguous() -> None:
    mask = [
        [True],
        [False],
        [False],
        [True],
    ]

    result = extract_trace_from_mask(mask)

    assert result[0].recoverability is TraceRecoverability.AMBIGUOUS
    assert result[0].pixel_y is None
    assert result[0].pixel_y_lower == 0
    assert result[0].pixel_y_upper == 3
    assert result[0].candidate_count == 2


def test_connected_thick_segment_is_not_ambiguous() -> None:
    mask = [
        [False],
        [True],
        [True],
        [False],
    ]

    result = extract_trace_from_mask(mask)

    assert result[0].recoverability is TraceRecoverability.OBSERVED
    assert result[0].pixel_y == pytest.approx(1.5)


def test_result_is_immutable() -> None:
    result = TraceColumnResult(
        pixel_x=0,
        pixel_y=1.0,
        pixel_y_lower=1,
        pixel_y_upper=1,
        candidate_count=1,
        recoverability=TraceRecoverability.OBSERVED,
    )

    with pytest.raises(Exception):
        result.pixel_x = 1  # type: ignore[misc]


def test_refuses_empty_mask() -> None:
    with pytest.raises(ValueError):
        extract_trace_from_mask([])


def test_refuses_zero_width_mask() -> None:
    with pytest.raises(ValueError):
        extract_trace_from_mask([[]])


def test_refuses_non_rectangular_mask() -> None:
    with pytest.raises(ValueError):
        extract_trace_from_mask(
            [
                [True, False],
                [True],
            ]
        )


def test_refuses_non_boolean_values() -> None:
    with pytest.raises(TypeError):
        extract_trace_from_mask(
            [
                [True, False],
                [False, 1],  # type: ignore[list-item]
            ]
        )


def test_preserves_column_order() -> None:
    mask = [
        [False, True, False],
        [True, False, True],
    ]

    result = extract_trace_from_mask(mask)

    assert tuple(item.pixel_x for item in result) == (0, 1, 2)


def test_output_length_equals_mask_width() -> None:
    mask = [
        [True, False, True, False, True],
        [False, True, False, True, False],
    ]

    result = extract_trace_from_mask(mask)

    assert len(result) == 5