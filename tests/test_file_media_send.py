from __future__ import annotations

from pathlib import Path

import pytest

from coffeecode_uploader import File, Media, Send, UploaderException


def test_file_upload_pdf(workdir, make_blob):
    f = File("uploads", "files", month_year_path=False)
    blob = make_blob("doc.pdf", "application/pdf", b"%PDF-")
    path = f.upload(blob, "Meu Documento")
    assert path == "uploads/files/meu-documento.pdf"
    assert Path(path).read_bytes().startswith(b"%PDF-")


def test_file_rejects_bad_mime(workdir, make_blob):
    f = File("uploads", "files", month_year_path=False)
    with pytest.raises(UploaderException):
        f.upload(make_blob("x.pdf", "text/plain"), "x")


def test_file_rejects_bad_extension(workdir, make_blob):
    f = File("uploads", "files", month_year_path=False)
    # mime allowed but extension not
    blob = make_blob("x.exe", "application/pdf")
    with pytest.raises(UploaderException):
        f.upload(blob, "x")


def test_media_upload_mp3(workdir, make_blob):
    m = Media("uploads", "medias", month_year_path=False)
    blob = make_blob("track.mp3", "audio/mpeg", b"ID3")
    path = m.upload(blob, "Musica")
    assert path == "uploads/medias/musica.mp3"


def test_media_rejects_invalid(workdir, make_blob):
    m = Media("uploads", "medias", month_year_path=False)
    with pytest.raises(UploaderException):
        m.upload(make_blob("track.wav", "audio/wav"), "x")


def test_send_with_custom_types(workdir, make_blob):
    s = Send(
        "uploads",
        "postscript",
        allow_types=["application/postscript"],
        extensions=["ai"],
        month_year_path=False,
    )
    blob = make_blob("logo.ai", "application/postscript", b"%!PS")
    path = s.upload(blob, "Logo")
    assert path == "uploads/postscript/logo.ai"


def test_send_rejects_outside_allowed(workdir, make_blob):
    s = Send(
        "uploads",
        "postscript",
        allow_types=["application/postscript"],
        extensions=["ai"],
        month_year_path=False,
    )
    with pytest.raises(UploaderException):
        s.upload(make_blob("x.pdf", "application/pdf"), "x")


def test_send_class_level_allow_lists_match_php(workdir):
    """Send mutates class-level allow lists (mirrors PHP self::$allowTypes).

    Constructing a new Send instance overrides the previous one's allow lists —
    same behavior as the original PHP package. Use distinct Send subclasses
    if you need isolation.
    """
    Send("uploads", "a", ["application/postscript"], ["ai"], month_year_path=False)
    assert "application/postscript" in Send.is_allowed()
    assert "ai" in Send.is_extension()

    Send("uploads", "b", ["application/pdf"], ["pdf"], month_year_path=False)
    # Latest construction wins (PHP-equivalent).
    assert "application/pdf" in Send.is_allowed()
    assert "application/postscript" not in Send.is_allowed()
