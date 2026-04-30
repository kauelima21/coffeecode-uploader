from __future__ import annotations

import html
import os
import re
import shutil
import time
import unicodedata
from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar


FileDict = dict[str, Any]


class Uploader(ABC):
    """Abstract base mirroring CoffeeCode\\Uploader\\Uploader (PHP).

    A file dict mirrors PHP ``$_FILES[...]`` and must contain:
        - ``name``: original filename (used for extension detection)
        - ``type``: MIME type
        - ``tmp_name``: filesystem path to the source/temporary file
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

    def multiple(self, input_name: str, files: dict[str, dict[str, list[Any]]]) -> list[FileDict]:
        """Convert PHP-style multi-input ``$_FILES`` into a list of single-file dicts."""
        bucket = files[input_name]
        keys = list(bucket.keys())
        count = len(bucket["name"])
        out: list[FileDict] = []
        for i in range(count):
            entry: FileDict = {}
            for key in keys:
                entry[key] = bucket[key][i]
            out.append(entry)
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

    def _ext(self, file: FileDict) -> None:
        ext = Path(file["name"]).suffix.lstrip(".").lower()
        self.ext = ext

    @staticmethod
    def _move(src: str, dst: str) -> None:
        """Move/copy uploaded file. Falls back to copy when src cannot be moved."""
        try:
            shutil.move(src, dst)
        except (OSError, shutil.SameFileError):
            shutil.copyfile(src, dst)
