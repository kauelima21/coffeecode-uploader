from __future__ import annotations

import pytest
from PIL import Image as PILImage

from coffeecode_uploader import Image, UploaderException


def test_upload_jpeg_resizes_to_target_width(workdir, make_jpeg):
    image = Image("uploads", "images", month_year_path=False)
    path = image.upload(make_jpeg(size=(1600, 1200)), "Foto Bonita", width=800)
    assert path == "uploads/images/foto-bonita.jpg"
    with PILImage.open(path) as out:
        assert out.size == (800, 600)
        assert out.format == "JPEG"


def test_upload_jpeg_keeps_size_when_target_larger(workdir, make_jpeg):
    image = Image("uploads", "images", month_year_path=False)
    path = image.upload(make_jpeg(size=(400, 300)), "small", width=2000)
    with PILImage.open(path) as out:
        assert out.size == (400, 300)


def test_upload_jpeg_from_stream(workdir, jpeg_stream):
    image = Image("uploads", "images", month_year_path=False)
    path = image.upload(jpeg_stream(size=(1024, 768)), "from-stream", width=512)
    assert path == "uploads/images/from-stream.jpg"
    with PILImage.open(path) as out:
        assert out.size == (512, 384)


def test_upload_png_preserves_alpha(workdir, make_png):
    image = Image("uploads", "images", month_year_path=False)
    path = image.upload(make_png(size=(200, 100)), "Logo", width=100)
    with PILImage.open(path) as out:
        assert out.format == "PNG"
        assert out.mode == "RGBA"
        assert out.size == (100, 50)


def test_upload_gif_passthrough(workdir, make_gif):
    image = Image("uploads", "images", month_year_path=False)
    src = make_gif(size=(120, 90))
    path = image.upload(src, "anim", width=60)
    with PILImage.open(path) as out:
        assert out.format == "GIF"
        assert out.size == (120, 90)


def test_upload_rejects_invalid_mime(workdir, make_blob):
    image = Image("uploads", "images", month_year_path=False)
    bad = make_blob("evil.exe", "application/x-msdownload", b"\x00")
    with pytest.raises(UploaderException, match="image type"):
        image.upload(bad, "evil")


def test_upload_rejects_empty_type(workdir, make_blob):
    image = Image("uploads", "images", month_year_path=False)
    bad = make_blob("anything.jpg", "", b"\x00")
    with pytest.raises(UploaderException, match="valid data"):
        image.upload(bad, "anything")


def test_collision_renames_with_timestamp(workdir, make_jpeg):
    image = Image("uploads", "images", month_year_path=False)
    image.upload(make_jpeg("a.jpg", size=(100, 100)), "same", width=100)
    second = image.upload(make_jpeg("b.jpg", size=(100, 100)), "same", width=100)
    assert second != "uploads/images/same.jpg"
    assert second.startswith("uploads/images/same-")
    assert second.endswith(".jpg")
