from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime

from tools.sos70_reconstruction.log_scale import (
    SolarXRayClass,
    classify_flux,
    flux_from_log_position,
)
from tools.sos70_reconstruction.time_scale import (
    TimeCalibration,
    datetime_from_pixel,
)


@dataclass(frozen=True)
class ChartCalibration:
    time_calibration: TimeCalibration
    plot_top_px: float
    plot_bottom_px: float
    flux_top_w_m2: float
    flux_bottom_w_m2: float

    def __post_init__(self) -> None:
        values = (
            self.plot_top_px,
            self.plot_bottom_px,
            self.flux_top_w_m2,
            self.flux_bottom_w_m2,
        )

        if not all(math.isfinite(value) for value in values):
            raise ValueError("all chart calibration values must be finite")

        if self.plot_bottom_px <= self.plot_top_px:
            raise ValueError(
                "plot_bottom_px must be greater than plot_top_px"
            )

        if self.flux_top_w_m2 <= 0.0:
            raise ValueError("flux_top_w_m2 must be greater than zero")

        if self.flux_bottom_w_m2 <= 0.0:
            raise ValueError("flux_bottom_w_m2 must be greater than zero")

        if self.flux_top_w_m2 <= self.flux_bottom_w_m2:
            raise ValueError(
                "flux_top_w_m2 must be greater than flux_bottom_w_m2"
            )


@dataclass(frozen=True)
class ReconstructedChartPoint:
    pixel_x: float
    pixel_y: float
    local_datetime: datetime
    utc_datetime: datetime
    estimated_flux_w_m2: float
    classification: SolarXRayClass


def reconstruct_chart_point(
    *,
    pixel_x: float,
    pixel_y: float,
    calibration: ChartCalibration,
) -> ReconstructedChartPoint:
    if not math.isfinite(pixel_x):
        raise ValueError("pixel_x must be finite")

    if not math.isfinite(pixel_y):
        raise ValueError("pixel_y must be finite")

    if (
        pixel_y < calibration.plot_top_px
        or pixel_y > calibration.plot_bottom_px
    ):
        raise ValueError("pixel_y must lie within the plot bounds")

    reconstructed_time = datetime_from_pixel(
        pixel_x=pixel_x,
        calibration=calibration.time_calibration,
    )

    estimated_flux = flux_from_log_position(
        pixel_y=pixel_y,
        plot_top_px=calibration.plot_top_px,
        plot_bottom_px=calibration.plot_bottom_px,
        flux_top_w_m2=calibration.flux_top_w_m2,
        flux_bottom_w_m2=calibration.flux_bottom_w_m2,
    )

    classification = classify_flux(estimated_flux)

    return ReconstructedChartPoint(
        pixel_x=pixel_x,
        pixel_y=pixel_y,
        local_datetime=reconstructed_time.local_datetime,
        utc_datetime=reconstructed_time.utc_datetime,
        estimated_flux_w_m2=estimated_flux,
        classification=classification,
    )