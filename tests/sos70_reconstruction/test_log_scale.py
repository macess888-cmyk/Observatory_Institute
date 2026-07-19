from __future__ import annotations

import math

import pytest

from tools.sos70_reconstruction.log_scale import (
    SolarXRayClass,
    classify_flux,
    flux_from_log_position,
    parse_solar_xray_class,
)


def test_flux_from_log_position_maps_top_boundary() -> None:
    result = flux_from_log_position(
        pixel_y=0.0,
        plot_top_px=0.0,
        plot_bottom_px=500.0,
        flux_top_w_m2=1e-3,
        flux_bottom_w_m2=1e-8,
    )

    assert result == pytest.approx(1e-3)


def test_flux_from_log_position_maps_bottom_boundary() -> None:
    result = flux_from_log_position(
        pixel_y=500.0,
        plot_top_px=0.0,
        plot_bottom_px=500.0,
        flux_top_w_m2=1e-3,
        flux_bottom_w_m2=1e-8,
    )

    assert result == pytest.approx(1e-8)


def test_flux_from_log_position_maps_midpoint_logarithmically() -> None:
    result = flux_from_log_position(
        pixel_y=250.0,
        plot_top_px=0.0,
        plot_bottom_px=500.0,
        flux_top_w_m2=1e-3,
        flux_bottom_w_m2=1e-8,
    )

    expected = math.sqrt(1e-3 * 1e-8)

    assert result == pytest.approx(expected)


def test_flux_mapping_is_not_linear() -> None:
    result = flux_from_log_position(
        pixel_y=250.0,
        plot_top_px=0.0,
        plot_bottom_px=500.0,
        flux_top_w_m2=1e-3,
        flux_bottom_w_m2=1e-8,
    )

    linear_midpoint = (1e-3 + 1e-8) / 2.0

    assert result != pytest.approx(linear_midpoint)


@pytest.mark.parametrize(
    ("flux", "expected_class"),
    [
        (1e-8, SolarXRayClass.A),
        (9.99e-8, SolarXRayClass.A),
        (1e-7, SolarXRayClass.B),
        (9.99e-7, SolarXRayClass.B),
        (1e-6, SolarXRayClass.C),
        (9.99e-6, SolarXRayClass.C),
        (1e-5, SolarXRayClass.M),
        (9.99e-5, SolarXRayClass.M),
        (1e-4, SolarXRayClass.X),
        (9.99e-4, SolarXRayClass.X),
        (1e-3, SolarXRayClass.X10_PLUS),
        (1e-2, SolarXRayClass.X10_PLUS),
    ],
)
def test_classify_flux_uses_standard_logarithmic_boundaries(
    flux: float,
    expected_class: SolarXRayClass,
) -> None:
    assert classify_flux(flux) is expected_class


@pytest.mark.parametrize(
    ("label", "expected_flux"),
    [
        ("A1.0", 1e-8),
        ("B2.5", 2.5e-7),
        ("C7.3", 7.3e-6),
        ("M1.0", 1e-5),
        ("M5.3", 5.3e-5),
        ("X1.0", 1e-4),
        ("X2.8", 2.8e-4),
        ("X10", 1e-3),
        ("X10.0", 1e-3),
    ],
)
def test_parse_solar_xray_class_returns_flux(
    label: str,
    expected_flux: float,
) -> None:
    result = parse_solar_xray_class(label)

    assert result.flux_w_m2 == pytest.approx(expected_flux)


def test_parse_solar_xray_class_preserves_normalized_label() -> None:
    result = parse_solar_xray_class("m5.3")

    assert result.normalized_label == "M5.3"
    assert result.classification is SolarXRayClass.M
    assert result.multiplier == pytest.approx(5.3)


@pytest.mark.parametrize(
    "label",
    [
        "",
        "M",
        "5.3",
        "Z1.0",
        "M-1",
        "M0",
        "M0.0",
        "X-2.8",
        "unknown",
    ],
)
def test_parse_solar_xray_class_refuses_invalid_labels(label: str) -> None:
    with pytest.raises(ValueError):
        parse_solar_xray_class(label)


@pytest.mark.parametrize(
    "invalid_flux",
    [
        0.0,
        -1e-5,
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
)
def test_classify_flux_refuses_non_physical_values(
    invalid_flux: float,
) -> None:
    with pytest.raises(ValueError):
        classify_flux(invalid_flux)


def test_flux_mapping_refuses_zero_height_plot() -> None:
    with pytest.raises(ValueError):
        flux_from_log_position(
            pixel_y=100.0,
            plot_top_px=100.0,
            plot_bottom_px=100.0,
            flux_top_w_m2=1e-3,
            flux_bottom_w_m2=1e-8,
        )


def test_flux_mapping_refuses_reversed_plot_geometry() -> None:
    with pytest.raises(ValueError):
        flux_from_log_position(
            pixel_y=100.0,
            plot_top_px=500.0,
            plot_bottom_px=0.0,
            flux_top_w_m2=1e-3,
            flux_bottom_w_m2=1e-8,
        )


def test_flux_mapping_refuses_invalid_flux_bounds() -> None:
    with pytest.raises(ValueError):
        flux_from_log_position(
            pixel_y=100.0,
            plot_top_px=0.0,
            plot_bottom_px=500.0,
            flux_top_w_m2=0.0,
            flux_bottom_w_m2=1e-8,
        )


def test_flux_mapping_refuses_pixel_outside_plot() -> None:
    with pytest.raises(ValueError):
        flux_from_log_position(
            pixel_y=501.0,
            plot_top_px=0.0,
            plot_bottom_px=500.0,
            flux_top_w_m2=1e-3,
            flux_bottom_w_m2=1e-8,
        )