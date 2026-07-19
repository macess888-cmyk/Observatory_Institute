from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum


class SolarXRayClass(Enum):
    A = "A"
    B = "B"
    C = "C"
    M = "M"
    X = "X"
    X10_PLUS = "X10+"


@dataclass(frozen=True)
class ParsedSolarXRayClass:
    normalized_label: str
    classification: SolarXRayClass
    multiplier: float
    flux_w_m2: float


_CLASS_BASE_FLUX: dict[str, float] = {
    "A": 1e-8,
    "B": 1e-7,
    "C": 1e-6,
    "M": 1e-5,
    "X": 1e-4,
}

_CLASS_PATTERN = re.compile(
    r"^(?P<class>[ABCMX])(?P<multiplier>\d+(?:\.\d+)?)$",
    re.IGNORECASE,
)


def _require_finite_positive(value: float, *, field_name: str) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{field_name} must be finite and greater than zero")


def classify_flux(flux_w_m2: float) -> SolarXRayClass:
    _require_finite_positive(flux_w_m2, field_name="flux_w_m2")

    if flux_w_m2 < 1e-7:
        return SolarXRayClass.A
    if flux_w_m2 < 1e-6:
        return SolarXRayClass.B
    if flux_w_m2 < 1e-5:
        return SolarXRayClass.C
    if flux_w_m2 < 1e-4:
        return SolarXRayClass.M
    if flux_w_m2 < 1e-3:
        return SolarXRayClass.X
    return SolarXRayClass.X10_PLUS


def flux_from_log_position(
    *,
    pixel_y: float,
    plot_top_px: float,
    plot_bottom_px: float,
    flux_top_w_m2: float,
    flux_bottom_w_m2: float,
) -> float:
    if not all(
        math.isfinite(value)
        for value in (
            pixel_y,
            plot_top_px,
            plot_bottom_px,
            flux_top_w_m2,
            flux_bottom_w_m2,
        )
    ):
        raise ValueError("all inputs must be finite")

    if plot_bottom_px <= plot_top_px:
        raise ValueError("plot_bottom_px must be greater than plot_top_px")

    if pixel_y < plot_top_px or pixel_y > plot_bottom_px:
        raise ValueError("pixel_y must lie within the plot bounds")

    _require_finite_positive(
        flux_top_w_m2,
        field_name="flux_top_w_m2",
    )
    _require_finite_positive(
        flux_bottom_w_m2,
        field_name="flux_bottom_w_m2",
    )

    if flux_top_w_m2 <= flux_bottom_w_m2:
        raise ValueError(
            "flux_top_w_m2 must be greater than flux_bottom_w_m2"
        )

    pixel_fraction = (
        pixel_y - plot_top_px
    ) / (
        plot_bottom_px - plot_top_px
    )

    log_top = math.log10(flux_top_w_m2)
    log_bottom = math.log10(flux_bottom_w_m2)

    log_flux = log_top + pixel_fraction * (log_bottom - log_top)

    return 10.0 ** log_flux


def parse_solar_xray_class(label: str) -> ParsedSolarXRayClass:
    normalized_input = label.strip().upper()
    match = _CLASS_PATTERN.fullmatch(normalized_input)

    if match is None:
        raise ValueError(f"invalid solar X-ray class label: {label!r}")

    class_letter = match.group("class").upper()
    multiplier = float(match.group("multiplier"))

    _require_finite_positive(
        multiplier,
        field_name="multiplier",
    )

    base_flux = _CLASS_BASE_FLUX[class_letter]
    flux_w_m2 = multiplier * base_flux
    classification = classify_flux(flux_w_m2)

    if class_letter != "X" and classification.value != class_letter:
        raise ValueError(
            "multiplier moves the value outside the declared class"
        )

    if class_letter == "X" and multiplier >= 10.0:
        classification = SolarXRayClass.X10_PLUS

    normalized_multiplier = (
        str(int(multiplier))
        if multiplier.is_integer()
        else str(multiplier).rstrip("0").rstrip(".")
    )

    normalized_label = f"{class_letter}{normalized_multiplier}"

    return ParsedSolarXRayClass(
        normalized_label=normalized_label,
        classification=classification,
        multiplier=multiplier,
        flux_w_m2=flux_w_m2,
    )