from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any, Iterator, Union

PathLike = Union[str, os.PathLike]
Source = Union[PathLike, IO[bytes]]


@dataclass
class UploadedFile:
    """Framework-agnostic upload payload.

    A unified abstraction over the various ways uploads arrive in Python:
        * a path on disk (pre-saved temp file, PHP-style)
        * a binary stream (Flask FileStorage, FastAPI UploadFile, raw BytesIO)

    Attributes:
        filename: Original client filename. Used for extension detection.
        content_type: MIME type (e.g. ``"image/jpeg"``).
        source: Either a filesystem path or a readable binary stream.
    """

    filename: str
    content_type: str
    source: Source

    @property
    def extension(self) -> str:
        return Path(self.filename).suffix.lstrip(".").lower()

    @property
    def is_path(self) -> bool:
        return isinstance(self.source, (str, os.PathLike))

    @contextmanager
    def open(self) -> Iterator[IO[bytes]]:
        """Yield a binary stream regardless of source kind."""
        if self.is_path:
            with open(self.source, "rb") as fp:  # type: ignore[arg-type]
                yield fp
        else:
            stream: IO[bytes] = self.source  # type: ignore[assignment]
            try:
                stream.seek(0)
            except (AttributeError, OSError):
                pass
            yield stream

    def save_to(self, dst: PathLike) -> None:
        """Copy contents to ``dst``. Does not delete the source."""
        import shutil

        if self.is_path:
            shutil.copyfile(self.source, dst)  # type: ignore[arg-type]
            return
        with self.open() as src, open(dst, "wb") as out:
            shutil.copyfileobj(src, out)

    @classmethod
    def from_path(
        cls,
        path: PathLike,
        content_type: str,
        filename: str | None = None,
    ) -> "UploadedFile":
        return cls(
            filename=filename or os.path.basename(os.fspath(path)),
            content_type=content_type,
            source=path,
        )

    @classmethod
    def from_stream(
        cls,
        stream: IO[bytes],
        filename: str,
        content_type: str,
    ) -> "UploadedFile":
        return cls(filename=filename, content_type=content_type, source=stream)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UploadedFile":
        """Adapter for legacy PHP ``$_FILES``-style dicts.

        Accepts ``{"name": ..., "type": ..., "tmp_name": ...}``.
        """
        return cls(
            filename=data["name"],
            content_type=data["type"],
            source=data["tmp_name"],
        )

    @classmethod
    def from_flask(cls, file_storage: Any) -> "UploadedFile":
        """Build from a Flask ``werkzeug.FileStorage`` (e.g. ``request.files['x']``)."""
        return cls(
            filename=file_storage.filename,
            content_type=file_storage.mimetype,
            source=file_storage.stream,
        )

    @classmethod
    def from_fastapi(cls, upload_file: Any) -> "UploadedFile":
        """Build from a FastAPI ``UploadFile``."""
        return cls(
            filename=upload_file.filename,
            content_type=upload_file.content_type,
            source=upload_file.file,
        )
