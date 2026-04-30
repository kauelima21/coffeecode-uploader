from __future__ import annotations

import html
import os
import re
import time
import unicodedata
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from .uploaded_file import UploadedFile


class Uploader(ABC):
    """Abstract base mirroring CoffeeCode\\Uploader\\Uploader (PHP).

    Subclasses validate ``UploadedFile`` instances against
    ``_allow_types`` (MIME) and ``_extensions`` (filename suffix), then
    persist the file under ``upload_dir/file_type_dir[/YYYY/MM]``.
    """

    _allow_types: ClassVar[list[str]] = []
    _extensions: ClassVar[list[str]] = []

    def __init__(
        self,
        upload_dir: str,
        file_type_dir: str,
        month_year_path: bool = True,
    ) -> None:
        self.path: str = ""
        self.name: str = ""
        self.ext: str = ""
        self.file: Any = None

        self._dir(upload_dir)
        self._dir(f"{upload_dir}/{file_type_dir}")
        self.path = f"{upload_dir}/{file_type_dir}"

        if month_year_path:
            self._path(f"{upload_dir}/{file_type_dir}")

    @classmethod
    def is_allowed(cls) -> list[str]:
        return list(cls._allow_types)

    @classmethod
    def is_extension(cls) -> list[str]:
        return list(cls._extensions)

    isAllowed = is_allowed
    isExtension = is_extension

    @staticmethod
    def multiple(files: list[Any]) -> list[UploadedFile]:
        """Normalize a list of framework upload objects to ``UploadedFile``.

        Accepts already-built ``UploadedFile`` instances, PHP-style dicts,
        Flask ``FileStorage`` and FastAPI ``UploadFile``. Anything else falls
        back to ``from_dict`` and will raise ``KeyError`` if shape differs.
        """
        out: list[UploadedFile] = []
        for item in files:
            if isinstance(item, UploadedFile):
                out.append(item)
            elif isinstance(item, dict):
                out.append(UploadedFile.from_dict(item))
            elif hasattr(item, "stream") and hasattr(item, "mimetype"):
                out.append(UploadedFile.from_flask(item))
            elif hasattr(item, "file") and hasattr(item, "content_type"):
                out.append(UploadedFile.from_fastapi(item))
            else:
                raise TypeError(f"Unsupported upload object: {type(item).__name__}")
        return out

    def _name(self, name: str) -> str:
        slug = self._slugify(name)
        candidate = f"{slug}.{self.ext}"
        full = os.path.join(self.path, candidate)
        if os.path.exists(full) and os.path.isfile(full):
            candidate = f"{slug}-{int(time.time())}.{self.ext}"
        self.name = candidate
        return self.name

    @staticmethod
    def _slugify(name: str) -> str:
        name = name.lower()
        name = html.escape(name, quote=False)
        normalized = unicodedata.normalize("NFKD", name)
        ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
        ascii_name = re.sub(r"[^a-z0-9]+", "-", ascii_name)
        ascii_name = re.sub(r"-+", "-", ascii_name).strip("-")
        return ascii_name or "file"

    @staticmethod
    def _dir(path: str, mode: int = 0o755) -> None:
        Path(path).mkdir(mode=mode, parents=True, exist_ok=True)

    def _path(self, base: str) -> None:
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        self._dir(f"{base}/{year}")
        self._dir(f"{base}/{year}/{month}")
        self.path = f"{base}/{year}/{month}"

    def _set_ext(self, file: UploadedFile) -> None:
        self.ext = file.extension

    @staticmethod
    def _validate(file: UploadedFile, allow_types: list[str], extensions: list[str]) -> None:
        from .exceptions import UploaderException

        if file.content_type not in allow_types or file.extension not in extensions:
            raise UploaderException("Not a valid file type or extension")
