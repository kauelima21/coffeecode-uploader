from __future__ import annotations

from typing import ClassVar

from .uploaded_file import UploadedFile
from .uploader import Uploader


class Media(Uploader):
    """Allow mp4 video and mp3 audio."""

    _allow_types: ClassVar[list[str]] = [
        "audio/mp3",
        "audio/mpeg",
        "video/mp4",
    ]

    _extensions: ClassVar[list[str]] = [
        "mp3",
        "mp4",
    ]

    def upload(self, media: UploadedFile, name: str) -> str:
        self._validate(media, self._allow_types, self._extensions)
        self._set_ext(media)
        self._name(name)
        dst = f"{self.path}/{self.name}"
        media.save_to(dst)
        return dst
