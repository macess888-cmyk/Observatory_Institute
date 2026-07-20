from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class TimeCalibration:
    plot_left_px: float
    plot_right_px: float
    local_start: datetime
    local_end: datetime

    def __post_init__(self) -> None:
        if not math.isfinite(self.plot_left_px):
            raise ValueError("plot_left_px must be finite")

        if not math.isfinite(self.plot_right_px):
            raise ValueError("plot_right_px must be finite")

        if self.plot_right_px <= self.plot_left_px:
            raise ValueError(
                "plot_right_px must be greater than plot_left_px"
            )

        if self.local_start.tzinfo is None:
            raise ValueError("local_start must be timezone-aware")

        if self.local_end.tzinfo is None:
            raise ValueError("local_end must be timezone-aware")

        if self.local_end <= self.local_start:
            raise ValueError(
                "local_end must be later than local_start"
            )


@dataclass(frozen=True)
class PixelDateTime:
    pixel_x: float
    local_datetime: datetime
    utc_datetime: datetime


def datetime_from_pixel(
    *,
    pixel_x: float,
    calibration: TimeCalibration,
) -> PixelDateTime:
    if not math.isfinite(pixel_x):
        raise ValueError("pixel_x must be finite")

    if (
        pixel_x < calibration.plot_left_px
        or pixel_x > calibration.plot_right_px
    ):
        raise ValueError("pixel_x must lie within the plot bounds")

    plot_width = (
        calibration.plot_right_px
        - calibration.plot_left_px
    )

    pixel_fraction = (
        pixel_x - calibration.plot_left_px
    ) / plot_width

    displayed_duration = (
        calibration.local_end
        - calibration.local_start
    )

    local_datetime = (
        calibration.local_start
        + displayed_duration * pixel_fraction
    )

    utc_datetime = local_datetime.astimezone(timezone.utc)

    return PixelDateTime(
        pixel_x=pixel_x,
        local_datetime=local_datetime,
        utc_datetime=utc_datetime,
    )