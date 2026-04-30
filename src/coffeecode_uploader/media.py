from __future__ import annotations

from typing import ClassVar

from .exceptions import UploaderException
from .uploader import FileDict, Uploader


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

    def upload(self, media: FileDict, name: str) -> str:
        self._ext(media)
        if media.get("type") not in self._allow_types or self.ext not in self._extensions:
            raise UploaderException("Not a valid media type or extension")
        self._name(name)
        dst = f"{self.path}/{self.name}"
        self._move(media["tmp_name"], dst)
        return dst
