from __future__ import annotations

from typing import ClassVar

from .exceptions import UploaderException
from .uploader import FileDict, Uploader


class File(Uploader):
    """Allow zip, rar, bzip, pdf, doc, docx, csv, xls, xlsx, ods, odt files."""

    _allow_types: ClassVar[list[str]] = [
        "application/zip",
        "application/x-rar-compressed",
        "application/x-bzip",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.text",
    ]

    _extensions: ClassVar[list[str]] = [
        "zip",
        "rar",
        "bz",
        "pdf",
        "doc",
        "docx",
        "csv",
        "xls",
        "xlsx",
        "ods",
        "odt",
    ]

    def upload(self, file: FileDict, name: str) -> str:
        self._ext(file)
        if file.get("type") not in self._allow_types or self.ext not in self._extensions:
            raise UploaderException("Not a valid file type or extension")
        self._name(name)
        dst = f"{self.path}/{self.name}"
        self._move(file["tmp_name"], dst)
        return dst
