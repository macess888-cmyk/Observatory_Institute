from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.sos70_reconstruction.chart_calibration import (
    ChartCalibration,
    ReconstructedChartPoint,
    reconstruct_chart_point,
)
from tools.sos70_reconstruction.log_scale import SolarXRayClass
from tools.sos70_reconstruction.time_scale import TimeCalibration


TOMSK = timezone(timedelta(hours=7))


def make_calibration() -> ChartCalibration:
    return ChartCalibration(
        time_calibration=TimeCalibration(
            plot_left_px=100.0,
            plot_right_px=800.0,
            local_start=datetime(2026, 7, 6, 0, 0, tzinfo=TOMSK),
            local_end=datetime(2026, 7, 13, 0, 0, tzinfo=TOMSK),
        ),
        plot_top_px=50.0,
        plot_bottom_px=550.0,
        flux_top_w_m2=1e-3,
        flux_bottom_w_m2=1e-8,
    )


def test_reconstruct_chart_point_combines_time_and_flux() -> None:
    calibration = make_calibration()

    result = reconstruct_chart_point(
        pixel_x=450.0,
        pixel_y=250.0,
        calibration=calibration,
    )

    assert isinstance(result, ReconstructedChartPoint)

    assert result.pixel_x == pytest.approx(450.0)
    assert result.pixel_y == pytest.approx(250.0)

    assert result.local_datetime == datetime(
        2026,
        7,
        9,
        12,
        0,
        tzinfo=TOMSK,
    )

    assert result.utc_datetime == datetime(
        2026,
        7,
        9,
        5,
        0,
        tzinfo=timezone.utc,
    )

    assert result.estimated_flux_w_m2 == pytest.approx(1e-5)
    assert result.classification is SolarXRayClass.M


def test_top_left_corner_maps_to_start_and_x10_plus() -> None:
    calibration = make_calibration()

    result = reconstruct_chart_point(
        pixel_x=100.0,
        pixel_y=50.0,
        calibration=calibration,
    )

    assert result.local_datetime == datetime(
        2026,
        7,
        6,
        0,
        0,
        tzinfo=TOMSK,
    )

    assert result.estimated_flux_w_m2 == pytest.approx(1e-3)
    assert result.classification is SolarXRayClass.X10_PLUS


def test_bottom_right_corner_maps_to_end_and_a_class() -> None:
    calibration = make_calibration()

    result = reconstruct_chart_point(
        pixel_x=800.0,
        pixel_y=550.0,
        calibration=calibration,
    )

    assert result.local_datetime == datetime(
        2026,
        7,
        13,
        0,
        0,
        tzinfo=TOMSK,
    )

    assert result.estimated_flux_w_m2 == pytest.approx(1e-8)
    assert result.classification is SolarXRayClass.A


def test_chart_calibration_is_immutable() -> None:
    calibration = make_calibration()

    with pytest.raises(Exception):
        calibration.plot_top_px = 0.0  # type: ignore[misc]


def test_reconstructed_point_is_immutable() -> None:
    result = reconstruct_chart_point(
        pixel_x=450.0,
        pixel_y=250.0,
        calibration=make_calibration(),
    )

    with pytest.raises(Exception):
        result.pixel_x = 451.0  # type: ignore[misc]


def test_refuses_zero_height_plot() -> None:
    with pytest.raises(ValueError):
        ChartCalibration(
            time_calibration=make_calibration().time_calibration,
            plot_top_px=50.0,
            plot_bottom_px=50.0,
            flux_top_w_m2=1e-3,
            flux_bottom_w_m2=1e-8,
        )


def test_refuses_reversed_vertical_geometry() -> None:
    with pytest.raises(ValueError):
        ChartCalibration(
            time_calibration=make_calibration().time_calibration,
            plot_top_px=550.0,
            plot_bottom_px=50.0,
            flux_top_w_m2=1e-3,
            flux_bottom_w_m2=1e-8,
        )


@pytest.mark.parametrize(
    ("flux_top", "flux_bottom"),
    [
        (0.0, 1e-8),
        (-1e-3, 1e-8),
        (1e-3, 0.0),
        (1e-3, -1e-8),
        (1e-8, 1e-3),
        (1e-5, 1e-5),
    ],
)
def test_refuses_invalid_flux_bounds(
    flux_top: float,
    flux_bottom: float,
) -> None:
    with pytest.raises(ValueError):
        ChartCalibration(
            time_calibration=make_calibration().time_calibration,
            plot_top_px=50.0,
            plot_bottom_px=550.0,
            flux_top_w_m2=flux_top,
            flux_bottom_w_m2=flux_bottom,
        )


@pytest.mark.parametrize(
    ("pixel_x", "pixel_y"),
    [
        (99.0, 250.0),
        (801.0, 250.0),
        (450.0, 49.0),
        (450.0, 551.0),
    ],
)
def test_refuses_point_outside_chart(
    pixel_x: float,
    pixel_y: float,
) -> None:
    with pytest.raises(ValueError):
        reconstruct_chart_point(
            pixel_x=pixel_x,
            pixel_y=pixel_y,
            calibration=make_calibration(),
        )