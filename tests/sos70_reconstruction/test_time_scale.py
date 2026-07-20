from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.sos70_reconstruction.time_scale import (
    TimeCalibration,
    datetime_from_pixel,
)


TOMSK = timezone(timedelta(hours=7))


def test_left_boundary_maps_to_start_time() -> None:
    calibration = TimeCalibration(
        plot_left_px=100.0,
        plot_right_px=800.0,
        local_start=datetime(2026, 7, 6, 0, 0, tzinfo=TOMSK),
        local_end=datetime(2026, 7, 13, 0, 0, tzinfo=TOMSK),
    )

    result = datetime_from_pixel(pixel_x=100.0, calibration=calibration)

    assert result.local_datetime == datetime(
        2026, 7, 6, 0, 0, tzinfo=TOMSK
    )
    assert result.utc_datetime == datetime(
        2026, 7, 5, 17, 0, tzinfo=timezone.utc
    )


def test_right_boundary_maps_to_end_time() -> None:
    calibration = TimeCalibration(
        plot_left_px=100.0,
        plot_right_px=800.0,
        local_start=datetime(2026, 7, 6, 0, 0, tzinfo=TOMSK),
        local_end=datetime(2026, 7, 13, 0, 0, tzinfo=TOMSK),
    )

    result = datetime_from_pixel(pixel_x=800.0, calibration=calibration)

    assert result.local_datetime == datetime(
        2026, 7, 13, 0, 0, tzinfo=TOMSK
    )
    assert result.utc_datetime == datetime(
        2026, 7, 12, 17, 0, tzinfo=timezone.utc
    )


def test_midpoint_maps_to_middle_of_interval() -> None:
    calibration = TimeCalibration(
        plot_left_px=100.0,
        plot_right_px=800.0,
        local_start=datetime(2026, 7, 6, 0, 0, tzinfo=TOMSK),
        local_end=datetime(2026, 7, 13, 0, 0, tzinfo=TOMSK),
    )

    result = datetime_from_pixel(pixel_x=450.0, calibration=calibration)

    assert result.local_datetime == datetime(
        2026, 7, 9, 12, 0, tzinfo=TOMSK
    )


@pytest.mark.parametrize(
    ("pixel_x", "expected_local"),
    [
        (100.0, datetime(2026, 7, 6, 0, 0, tzinfo=TOMSK)),
        (200.0, datetime(2026, 7, 7, 0, 0, tzinfo=TOMSK)),
        (300.0, datetime(2026, 7, 8, 0, 0, tzinfo=TOMSK)),
        (400.0, datetime(2026, 7, 9, 0, 0, tzinfo=TOMSK)),
        (500.0, datetime(2026, 7, 10, 0, 0, tzinfo=TOMSK)),
        (600.0, datetime(2026, 7, 11, 0, 0, tzinfo=TOMSK)),
        (700.0, datetime(2026, 7, 12, 0, 0, tzinfo=TOMSK)),
        (800.0, datetime(2026, 7, 13, 0, 0, tzinfo=TOMSK)),
    ],
)
def test_daily_tick_alignment(
    pixel_x: float,
    expected_local: datetime,
) -> None:
    calibration = TimeCalibration(
        plot_left_px=100.0,
        plot_right_px=800.0,
        local_start=datetime(2026, 7, 6, 0, 0, tzinfo=TOMSK),
        local_end=datetime(2026, 7, 13, 0, 0, tzinfo=TOMSK),
    )

    result = datetime_from_pixel(
        pixel_x=pixel_x,
        calibration=calibration,
    )

    assert result.local_datetime == expected_local


def test_refuses_zero_width_plot() -> None:
    with pytest.raises(ValueError):
        TimeCalibration(
            plot_left_px=100.0,
            plot_right_px=100.0,
            local_start=datetime(2026, 7, 6, tzinfo=TOMSK),
            local_end=datetime(2026, 7, 13, tzinfo=TOMSK),
        )


def test_refuses_reversed_plot_geometry() -> None:
    with pytest.raises(ValueError):
        TimeCalibration(
            plot_left_px=800.0,
            plot_right_px=100.0,
            local_start=datetime(2026, 7, 6, tzinfo=TOMSK),
            local_end=datetime(2026, 7, 13, tzinfo=TOMSK),
        )


def test_refuses_invalid_time_window() -> None:
    with pytest.raises(ValueError):
        TimeCalibration(
            plot_left_px=100.0,
            plot_right_px=800.0,
            local_start=datetime(2026, 7, 13, tzinfo=TOMSK),
            local_end=datetime(2026, 7, 6, tzinfo=TOMSK),
        )


def test_refuses_naive_datetime() -> None:
    with pytest.raises(ValueError):
        TimeCalibration(
            plot_left_px=100.0,
            plot_right_px=800.0,
            local_start=datetime(2026, 7, 6),
            local_end=datetime(2026, 7, 13),
        )


def test_refuses_pixel_outside_plot() -> None:
    calibration = TimeCalibration(
        plot_left_px=100.0,
        plot_right_px=800.0,
        local_start=datetime(2026, 7, 6, tzinfo=TOMSK),
        local_end=datetime(2026, 7, 13, tzinfo=TOMSK),
    )

    with pytest.raises(ValueError):
        datetime_from_pixel(
            pixel_x=99.0,
            calibration=calibration,
        )