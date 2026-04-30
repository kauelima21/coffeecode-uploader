from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image as PILImage

from coffeecode_uploader import UploadedFile


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def make_jpeg(tmp_path):
    def _make(name: str = "src.jpg", size=(800, 600), color=(255, 0, 0)) -> UploadedFile:
        path = tmp_path / name
        img = PILImage.new("RGB", size, color)
        img.save(path, format="JPEG")
        return UploadedFile.from_path(path, content_type="image/jpeg", filename=name)
    return _make


@pytest.fixture
def make_png(tmp_path):
    def _make(name: str = "src.png", size=(400, 300)) -> UploadedFile:
        path = tmp_path / name
        img = PILImage.new("RGBA", size, (0, 255, 0, 128))
        img.save(path, format="PNG")
        return UploadedFile.from_path(path, content_type="image/png", filename=name)
    return _make


@pytest.fixture
def make_gif(tmp_path):
    def _make(name: str = "src.gif", size=(120, 90)) -> UploadedFile:
        path = tmp_path / name
        img = PILImage.new("P", size, 0)
        img.save(path, format="GIF")
        return UploadedFile.from_path(path, content_type="image/gif", filename=name)
    return _make


@pytest.fixture
def make_blob(tmp_path):
    def _make(name: str, mime: str, content: bytes = b"data") -> UploadedFile:
        path = tmp_path / name
        path.write_bytes(content)
        return UploadedFile.from_path(path, content_type=mime, filename=name)
    return _make


@pytest.fixture
def jpeg_stream():
    """Build an UploadedFile backed by an in-memory BytesIO stream."""
    def _make(name: str = "stream.jpg", size=(640, 480)) -> UploadedFile:
        buf = BytesIO()
        PILImage.new("RGB", size, (0, 0, 255)).save(buf, format="JPEG")
        buf.seek(0)
        return UploadedFile.from_stream(buf, filename=name, content_type="image/jpeg")
    return _make
