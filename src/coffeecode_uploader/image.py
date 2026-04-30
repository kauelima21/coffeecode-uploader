from __future__ import annotations

from typing import ClassVar, Optional

from PIL import Image as PILImage

from .exceptions import UploaderException
from .uploader import FileDict, Uploader


class Image(Uploader):
    """Allow jpg, png and gif images. Resizes via Pillow (replaces PHP GD)."""

    _allow_types: ClassVar[list[str]] = [
        "image/jpeg",
        "image/png",
        "image/gif",
    ]

    _extensions: ClassVar[list[str]] = [
        "jpg",
        "png",
        "gif",
    ]

    def upload(
        self,
        image: FileDict,
        name: str,
        width: int = 2000,
        quality: Optional[dict[str, int]] = None,
    ) -> str:
        if not image.get("type"):
            raise UploaderException("Not a valid data from image")

        if not self._image_create(image):
            raise UploaderException("Not a valid image type or extension")

        self._name(name)
        dst = f"{self.path}/{self.name}"

        if self.ext == "gif":
            self._move(image["tmp_name"], dst)
            return dst

        q = quality if quality is not None else {"jpg": 75, "png": 5}
        self._image_generate(width, q)
        return dst

    def _image_create(self, image: FileDict) -> bool:
        mime = image.get("type")
        tmp = image["tmp_name"]

        if mime == "image/jpeg":
            self.file = PILImage.open(tmp)
            self.ext = "jpg"
            return True

        if mime == "image/png":
            self.file = PILImage.open(tmp)
            self.ext = "png"
            return True

        if mime == "image/gif":
            self.ext = "gif"
            return True

        return False

    def _image_generate(self, width: int, quality: dict[str, int]) -> None:
        src: PILImage.Image = self.file
        file_x, file_y = src.size
        image_w = width if width < file_x else file_x
        image_h = int((image_w * file_y) / file_x)
        dst_path = f"{self.path}/{self.name}"

        if self.ext == "jpg":
            converted = src.convert("RGB") if src.mode != "RGB" else src
            resized = converted.resize((image_w, image_h), PILImage.LANCZOS)
            resized.save(dst_path, format="JPEG", quality=int(quality["jpg"]))
            if resized is not converted:
                converted.close()
            resized.close()

        elif self.ext == "png":
            converted = src.convert("RGBA") if src.mode != "RGBA" else src
            resized = converted.resize((image_w, image_h), PILImage.LANCZOS)
            resized.save(dst_path, format="PNG", compress_level=int(quality["png"]))
            if resized is not converted:
                converted.close()
            resized.close()

        src.close()
        self.file = None
