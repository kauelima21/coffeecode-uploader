from __future__ import annotations

from .uploaded_file import UploadedFile
from .uploader import Uploader


class Send(Uploader):
    """Generic upload with caller-provided allowed types and extensions."""

    def __init__(
        self,
        upload_dir: str,
        file_type_dir: str,
        allow_types: list[str],
        extensions: list[str],
        month_year_path: bool = True,
    ) -> None:
        super().__init__(upload_dir, file_type_dir, month_year_path)
        # Mirror PHP: self::$allowTypes assignment is class-level (late static binding).
        # Constructing a new Send instance overrides the previous one's allow lists.
        Send._allow_types = list(allow_types)
        Send._extensions = list(extensions)

    def upload(self, file: UploadedFile, name: str) -> str:
        self._validate(file, self._allow_types, self._extensions)
        self._set_ext(file)
        self._name(name)
        dst = f"{self.path}/{self.name}"
        file.save_to(dst)
        return dst
