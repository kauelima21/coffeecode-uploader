from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from coffeecode_uploader import UploadedFile


def test_from_path_infers_filename(tmp_path):
    p = tmp_path / "report.pdf"
    p.write_bytes(b"%PDF-")
    f = UploadedFile.from_path(p, content_type="application/pdf")
    assert f.filename == "report.pdf"
    assert f.content_type == "application/pdf"
    assert f.extension == "pdf"
    assert f.is_path is True


def test_from_stream():
    buf = BytesIO(b"hello")
    f = UploadedFile.from_stream(buf, filename="x.txt", content_type="text/plain")
    assert f.is_path is False
    assert f.extension == "txt"
    with f.open() as src:
        assert src.read() == b"hello"


def test_from_dict_php_legacy(tmp_path):
    src = tmp_path / "tmp.bin"
    src.write_bytes(b"x")
    f = UploadedFile.from_dict({
        "name": "doc.pdf",
        "type": "application/pdf",
        "tmp_name": str(src),
    })
    assert f.filename == "doc.pdf"
    assert f.content_type == "application/pdf"
    assert f.source == str(src)


def test_from_flask_adapter():
    fake = SimpleNamespace(
        filename="upload.png",
        mimetype="image/png",
        stream=BytesIO(b"data"),
    )
    f = UploadedFile.from_flask(fake)
    assert f.filename == "upload.png"
    assert f.content_type == "image/png"


def test_from_fastapi_adapter():
    fake = SimpleNamespace(
        filename="clip.mp4",
        content_type="video/mp4",
        file=BytesIO(b"data"),
    )
    f = UploadedFile.from_fastapi(fake)
    assert f.filename == "clip.mp4"
    assert f.content_type == "video/mp4"


def test_save_to_path_source(tmp_path):
    src = tmp_path / "in.bin"
    src.write_bytes(b"contents")
    dst = tmp_path / "out.bin"
    f = UploadedFile.from_path(src, content_type="application/octet-stream")
    f.save_to(dst)
    assert dst.read_bytes() == b"contents"
    # Source must NOT be deleted.
    assert src.exists()


def test_save_to_stream_source(tmp_path):
    buf = BytesIO(b"streamed")
    dst = tmp_path / "out.bin"
    f = UploadedFile.from_stream(buf, filename="x.bin", content_type="application/octet-stream")
    f.save_to(dst)
    assert dst.read_bytes() == b"streamed"


def test_open_resets_stream_position():
    buf = BytesIO(b"abc")
    buf.read()  # advance
    f = UploadedFile.from_stream(buf, filename="x.bin", content_type="application/octet-stream")
    with f.open() as src:
        assert src.read() == b"abc"
