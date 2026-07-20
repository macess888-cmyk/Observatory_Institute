from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError


RGBPixel = tuple[int, int, int]
RGBMatrix = tuple[tuple[RGBPixel, ...], ...]


@dataclass(frozen=True)
class LoadedImage:
    source_path: Path
    width: int
    height: int
    mode: str
    file_size_bytes: int
    sha256: str
    pixels: RGBMatrix


_SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp",
}


def _compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def _to_rgb_matrix(image: Image.Image) -> RGBMatrix:
    rgb_image = image.convert("RGB")
    width, height = rgb_image.size

    flat_pixels = tuple(rgb_image.get_flattened_data())

    rows: list[tuple[RGBPixel, ...]] = []

    for row_index in range(height):
        start = row_index * width
        end = start + width

        row = tuple(
            (
                int(pixel[0]),
                int(pixel[1]),
                int(pixel[2]),
            )
            for pixel in flat_pixels[start:end]
        )

        rows.append(row)

    return tuple(rows)


def load_rgb_image(path: str | Path) -> LoadedImage:
    source_path = Path(path).expanduser().resolve()

    if not source_path.exists():
        raise FileNotFoundError(source_path)

    if not source_path.is_file():
        raise ValueError("path must reference a regular file")

    if source_path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"unsupported image extension: {source_path.suffix}"
        )

    file_size_bytes = source_path.stat().st_size
    sha256 = _compute_sha256(source_path)

    try:
        with Image.open(source_path) as image:
            image.load()

            width, height = image.size

            if width <= 0 or height <= 0:
                raise ValueError(
                    "image dimensions must be greater than zero"
                )

            pixels = _to_rgb_matrix(image)

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError(
            f"unable to load image: {source_path}"
        ) from exc

    return LoadedImage(
        source_path=source_path,
        width=width,
        height=height,
        mode="RGB",
        file_size_bytes=file_size_bytes,
        sha256=sha256,
        pixels=pixels,
    )