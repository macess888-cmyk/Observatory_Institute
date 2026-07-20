from __future__ import annotations

import pytest

from tools.sos70_reconstruction.trace_mask import (
    RGBColour,
    TraceMaskConfig,
    build_trace_mask,
)


def test_exact_target_colour_match() -> None:
    image = (
        ((255, 0, 0), (0, 0, 0)),
        ((0, 0, 0), (255, 0, 0)),
    )

    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == (
        (True, False),
        (False, True),
    )


def test_colour_distance_tolerance_accepts_near_red() -> None:
    image = (
        ((250, 5, 3),),
    )

    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=10.0,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == ((True,),)


def test_colour_distance_tolerance_rejects_distant_colour() -> None:
    image = (
        ((200, 50, 50),),
    )

    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=20.0,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == ((False,),)


def test_multiple_target_colours_are_supported() -> None:
    image = (
        ((255, 0, 0), (255, 90, 0), (0, 0, 0)),
    )

    config = TraceMaskConfig(
        target_colours=(
            RGBColour(255, 0, 0),
            RGBColour(255, 90, 0),
        ),
        colour_distance_tolerance=0.0,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == ((True, True, False),)


def test_plot_region_crop_preserves_requested_rectangle() -> None:
    image = (
        ((0, 0, 0), (0, 0, 0), (0, 0, 0)),
        ((0, 0, 0), (255, 0, 0), (0, 0, 0)),
        ((0, 0, 0), (0, 0, 0), (255, 0, 0)),
    )

    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
        crop_left_px=1,
        crop_top_px=1,
        crop_right_px=3,
        crop_bottom_px=3,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == (
        (True, False),
        (False, True),
    )


def test_background_is_rejected() -> None:
    image = (
        ((0, 0, 0), (25, 25, 25), (255, 0, 0)),
    )

    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=5.0,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == ((False, False, True),)


def test_white_gridline_is_rejected() -> None:
    image = (
        ((255, 255, 255), (255, 0, 0)),
    )

    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=10.0,
    )

    result = build_trace_mask(image=image, config=config)

    assert result == ((False, True),)


def test_result_is_deterministic() -> None:
    image = (
        ((255, 0, 0), (255, 100, 0)),
        ((0, 0, 0), (250, 5, 5)),
    )

    config = TraceMaskConfig(
        target_colours=(
            RGBColour(255, 0, 0),
            RGBColour(255, 100, 0),
        ),
        colour_distance_tolerance=10.0,
    )

    first = build_trace_mask(image=image, config=config)
    second = build_trace_mask(image=image, config=config)

    assert first == second


def test_refuses_empty_image() -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
    )

    with pytest.raises(ValueError):
        build_trace_mask(image=(), config=config)


def test_refuses_zero_width_image() -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
    )

    with pytest.raises(ValueError):
        build_trace_mask(image=((),), config=config)


def test_refuses_non_rectangular_image() -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
    )

    image = (
        ((255, 0, 0), (0, 0, 0)),
        ((255, 0, 0),),
    )

    with pytest.raises(ValueError):
        build_trace_mask(image=image, config=config)


@pytest.mark.parametrize(
    "colour",
    [
        (-1, 0, 0),
        (256, 0, 0),
        (0, -1, 0),
        (0, 256, 0),
        (0, 0, -1),
        (0, 0, 256),
    ],
)
def test_refuses_invalid_image_channel_values(
    colour: tuple[int, int, int],
) -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
    )

    with pytest.raises(ValueError):
        build_trace_mask(image=((colour,),), config=config)


def test_refuses_non_integer_image_channels() -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
    )

    image = (
        ((255.0, 0, 0),),  # type: ignore[list-item]
    )

    with pytest.raises(TypeError):
        build_trace_mask(image=image, config=config)


def test_refuses_empty_target_colour_set() -> None:
    with pytest.raises(ValueError):
        TraceMaskConfig(
            target_colours=(),
            colour_distance_tolerance=0.0,
        )


def test_refuses_negative_tolerance() -> None:
    with pytest.raises(ValueError):
        TraceMaskConfig(
            target_colours=(RGBColour(255, 0, 0),),
            colour_distance_tolerance=-1.0,
        )


def test_refuses_invalid_crop_bounds() -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
        crop_left_px=2,
        crop_top_px=0,
        crop_right_px=1,
        crop_bottom_px=1,
    )

    image = (
        ((255, 0, 0), (255, 0, 0)),
    )

    with pytest.raises(ValueError):
        build_trace_mask(image=image, config=config)


def test_refuses_crop_outside_image() -> None:
    config = TraceMaskConfig(
        target_colours=(RGBColour(255, 0, 0),),
        colour_distance_tolerance=0.0,
        crop_left_px=0,
        crop_top_px=0,
        crop_right_px=3,
        crop_bottom_px=1,
    )

    image = (
        ((255, 0, 0), (255, 0, 0)),
    )

    with pytest.raises(ValueError):
        build_trace_mask(image=image, config=config)