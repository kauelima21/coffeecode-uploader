from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from coffeecode_uploader import File, UploadedFile
from coffeecode_uploader.uploader import Uploader


def test_slugify_strips_accents_and_specials():
    assert Uploader._slugify("Olá Mundo!") == "ola-mundo"
    assert Uploader._slugify("  Foo   Bar  ") == "foo-bar"
    assert Uploader._slugify("Relatório (2024)/v2") == "relatorio-2024-v2"
    assert Uploader._slugify("---weird---name---") == "weird-name"
    assert Uploader._slugify("////") == "file"


def test_constructor_creates_year_month_path(workdir):
    f = File("uploads", "files")
    now = datetime.now()
    expected = Path(f"uploads/files/{now.strftime('%Y')}/{now.strftime('%m')}")
    assert expected.is_dir()
    assert f.path == f"uploads/files/{now.strftime('%Y')}/{now.strftime('%m')}"


def test_constructor_without_year_month_path(workdir):
    f = File("uploads", "files", month_year_path=False)
    assert f.path == "uploads/files"
    assert Path("uploads/files").is_dir()
    assert not Path(f"uploads/files/{datetime.now().strftime('%Y')}").exists()


def test_is_allowed_and_is_extension_classmethods():
    assert "application/pdf" in File.is_allowed()
    assert "pdf" in File.is_extension()
    assert File.isAllowed() == File.is_allowed()
    assert File.isExtension() == File.is_extension()


def test_multiple_normalizes_mixed_inputs(tmp_path):
    a = tmp_path / "a.pdf"
    a.write_bytes(b"%PDF-")
    items = [
        {"name": "b.pdf", "type": "application/pdf", "tmp_name": str(a)},
        UploadedFile.from_path(a, content_type="application/pdf", filename="c.pdf"),
        SimpleNamespace(filename="d.pdf", mimetype="application/pdf", stream=BytesIO(b"x")),
    ]
    out = Uploader.multiple(items)
    assert [u.filename for u in out] == ["b.pdf", "c.pdf", "d.pdf"]
    assert all(isinstance(u, UploadedFile) for u in out)


def test_multiple_rejects_unknown_type():
    with pytest.raises(TypeError):
        Uploader.multiple([42])
