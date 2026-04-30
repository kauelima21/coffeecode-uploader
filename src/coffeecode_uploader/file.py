from __future__ import annotations

from typing import ClassVar

from .uploaded_file import UploadedFile
from .uploader import Uploader


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

    def upload(self, file: UploadedFile, name: str) -> str:
        self._validate(file, self._allow_types, self._extensions)
        self._set_ext(file)
        self._name(name)
        dst = f"{self.path}/{self.name}"
        file.save_to(dst)
        return dst
