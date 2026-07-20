from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from tools.sos70_reconstruction.image_loader import (
    LoadedImage,
    load_rgb_image,
)


def test_loads_rgb_jpeg_as_immutable_matrix(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.jpg"

    image = Image.new("RGB", (2, 2))
    image.putdata(
        [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 255),
        ]
    )
    image.save(image_path, format="JPEG", quality=100, subsampling=0)

    result = load_rgb_image(image_path)

    assert isinstance(result, LoadedImage)
    assert result.width == 2
    assert result.height == 2
    assert result.mode == "RGB"
    assert result.source_path == image_path.resolve()

    assert len(result.pixels) == 2
    assert len(result.pixels[0]) == 2


def test_loads_png_and_converts_to_rgb(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    image = Image.new("RGBA", (1, 1), (255, 0, 0, 128))
    image.save(image_path)

    result = load_rgb_image(image_path)

    assert result.mode == "RGB"
    assert result.width == 1
    assert result.height == 1
    assert result.pixels == (((255, 0, 0),),)


def test_pixel_matrix_matches_image_dimensions(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    image = Image.new("RGB", (3, 2), (10, 20, 30))
    image.save(image_path)

    result = load_rgb_image(image_path)

    assert len(result.pixels) == result.height
    assert all(len(row) == result.width for row in result.pixels)


def test_result_is_immutable(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    Image.new("RGB", (1, 1), (1, 2, 3)).save(image_path)

    result = load_rgb_image(image_path)

    with pytest.raises(Exception):
        result.width = 2  # type: ignore[misc]


def test_pixels_are_tuple_backed(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    Image.new("RGB", (1, 1), (1, 2, 3)).save(image_path)

    result = load_rgb_image(image_path)

    assert isinstance(result.pixels, tuple)
    assert isinstance(result.pixels[0], tuple)
    assert isinstance(result.pixels[0][0], tuple)


def test_refuses_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.jpg"

    with pytest.raises(FileNotFoundError):
        load_rgb_image(missing_path)


def test_refuses_directory_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        load_rgb_image(tmp_path)


def test_refuses_unsupported_file_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("not an image", encoding="utf-8")

    with pytest.raises(ValueError):
        load_rgb_image(file_path)


def test_refuses_corrupted_image(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.jpg"
    image_path.write_bytes(b"not-a-valid-image")

    with pytest.raises(ValueError):
        load_rgb_image(image_path)


def test_records_file_size(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    Image.new("RGB", (1, 1), (1, 2, 3)).save(image_path)

    result = load_rgb_image(image_path)

    assert result.file_size_bytes == image_path.stat().st_size


def test_records_sha256(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    Image.new("RGB", (1, 1), (1, 2, 3)).save(image_path)

    result = load_rgb_image(image_path)

    assert len(result.sha256) == 64
    assert all(character in "0123456789abcdef" for character in result.sha256)


def test_repeated_load_is_deterministic(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"

    Image.new("RGB", (2, 2), (12, 34, 56)).save(image_path)

    first = load_rgb_image(image_path)
    second = load_rgb_image(image_path)

    assert first == second