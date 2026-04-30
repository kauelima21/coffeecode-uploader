from __future__ import annotations

import io
import shutil
from pathlib import Path

import pytest
from PIL import Image as PILImage


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def make_jpeg(tmp_path):
    def _make(name: str = "src.jpg", size=(800, 600), color=(255, 0, 0)) -> dict:
        path = tmp_path / name
        img = PILImage.new("RGB", size, color)
        img.save(path, format="JPEG")
        return {"name": name, "type": "image/jpeg", "tmp_name": str(path)}
    return _make


@pytest.fixture
def make_png(tmp_path):
    def _make(name: str = "src.png", size=(400, 300)) -> dict:
        path = tmp_path / name
        img = PILImage.new("RGBA", size, (0, 255, 0, 128))
        img.save(path, format="PNG")
        return {"name": name, "type": "image/png", "tmp_name": str(path)}
    return _make


@pytest.fixture
def make_gif(tmp_path):
    def _make(name: str = "src.gif", size=(120, 90)) -> dict:
        path = tmp_path / name
        img = PILImage.new("P", size, 0)
        img.save(path, format="GIF")
        return {"name": name, "type": "image/gif", "tmp_name": str(path)}
    return _make


@pytest.fixture
def make_blob(tmp_path):
    def _make(name: str, mime: str, content: bytes = b"data") -> dict:
        path = tmp_path / name
        path.write_bytes(content)
        return {"name": name, "type": mime, "tmp_name": str(path)}
    return _make
