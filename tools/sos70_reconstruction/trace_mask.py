from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RGBColour:
    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        for field_name, value in (
            ("red", self.red),
            ("green", self.green),
            ("blue", self.blue),
        ):
            if type(value) is not int:
                raise TypeError(f"{field_name} must be int")

            if value < 0 or value > 255:
                raise ValueError(
                    f"{field_name} must be between 0 and 255"
                )


@dataclass(frozen=True)
class TraceMaskConfig:
    target_colours: tuple[RGBColour, ...]
    colour_distance_tolerance: float
    crop_left_px: int | None = None
    crop_top_px: int | None = None
    crop_right_px: int | None = None
    crop_bottom_px: int | None = None

    def __post_init__(self) -> None:
        if not self.target_colours:
            raise ValueError("target_colours must not be empty")

        if not math.isfinite(self.colour_distance_tolerance):
            raise ValueError(
                "colour_distance_tolerance must be finite"
            )

        if self.colour_distance_tolerance < 0.0:
            raise ValueError(
                "colour_distance_tolerance must be non-negative"
            )

        for field_name, value in (
            ("crop_left_px", self.crop_left_px),
            ("crop_top_px", self.crop_top_px),
            ("crop_right_px", self.crop_right_px),
            ("crop_bottom_px", self.crop_bottom_px),
        ):
            if value is not None:
                if type(value) is not int:
                    raise TypeError(f"{field_name} must be int or None")

                if value < 0:
                    raise ValueError(
                        f"{field_name} must be non-negative"
                    )


ImagePixel = tuple[int, int, int]
ImageMatrix = Sequence[Sequence[ImagePixel]]
TraceMask = tuple[tuple[bool, ...], ...]


def _validate_channel(value: object, *, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be int")

    integer_value = int(value)

    if integer_value < 0 or integer_value > 255:
        raise ValueError(
            f"{field_name} must be between 0 and 255"
        )

    return integer_value


def _validate_pixel(pixel: object) -> ImagePixel:
    if not isinstance(pixel, tuple):
        raise TypeError("each pixel must be an RGB tuple")

    if len(pixel) != 3:
        raise ValueError("each pixel must contain exactly 3 channels")

    red = _validate_channel(pixel[0], field_name="red")
    green = _validate_channel(pixel[1], field_name="green")
    blue = _validate_channel(pixel[2], field_name="blue")

    return red, green, blue


def _validate_image(image: ImageMatrix) -> tuple[int, int]:
    if len(image) == 0:
        raise ValueError("image must contain at least one row")

    width = len(image[0])

    if width == 0:
        raise ValueError("image must contain at least one column")

    for row in image:
        if len(row) != width:
            raise ValueError("image must be rectangular")

        for pixel in row:
            _validate_pixel(pixel)

    return len(image), width


def _resolve_crop(
    *,
    image_height: int,
    image_width: int,
    config: TraceMaskConfig,
) -> tuple[int, int, int, int]:
    left = 0 if config.crop_left_px is None else config.crop_left_px
    top = 0 if config.crop_top_px is None else config.crop_top_px
    right = (
        image_width
        if config.crop_right_px is None
        else config.crop_right_px
    )
    bottom = (
        image_height
        if config.crop_bottom_px is None
        else config.crop_bottom_px
    )

    if right <= left:
        raise ValueError("crop_right_px must be greater than crop_left_px")

    if bottom <= top:
        raise ValueError(
            "crop_bottom_px must be greater than crop_top_px"
        )

    if right > image_width or bottom > image_height:
        raise ValueError("crop bounds must lie within the image")

    return left, top, right, bottom


def _colour_distance(
    pixel: ImagePixel,
    target: RGBColour,
) -> float:
    red_delta = pixel[0] - target.red
    green_delta = pixel[1] - target.green
    blue_delta = pixel[2] - target.blue

    return math.sqrt(
        red_delta * red_delta
        + green_delta * green_delta
        + blue_delta * blue_delta
    )


def _matches_target(
    *,
    pixel: ImagePixel,
    config: TraceMaskConfig,
) -> bool:
    return any(
        _colour_distance(pixel, target)
        <= config.colour_distance_tolerance
        for target in config.target_colours
    )


def build_trace_mask(
    *,
    image: ImageMatrix,
    config: TraceMaskConfig,
) -> TraceMask:
    image_height, image_width = _validate_image(image)

    left, top, right, bottom = _resolve_crop(
        image_height=image_height,
        image_width=image_width,
        config=config,
    )

    rows: list[tuple[bool, ...]] = []

    for pixel_y in range(top, bottom):
        row: list[bool] = []

        for pixel_x in range(left, right):
            pixel = _validate_pixel(image[pixel_y][pixel_x])

            row.append(
                _matches_target(
                    pixel=pixel,
                    config=config,
                )
            )

        rows.append(tuple(row))

    return tuple(rows)