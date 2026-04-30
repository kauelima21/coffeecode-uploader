from __future__ import annotations

from .exceptions import UploaderException
from .uploader import FileDict, Uploader


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

    def upload(self, file: FileDict, name: str) -> str:
        self._ext(file)
        if file.get("type") not in self._allow_types or self.ext not in self._extensions:
            raise UploaderException("Not a valid file type or extension")
        self._name(name)
        dst = f"{self.path}/{self.name}"
        self._move(file["tmp_name"], dst)
        return dst
