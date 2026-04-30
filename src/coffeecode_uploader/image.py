from __future__ import annotations

from typing import ClassVar, Optional

from PIL import Image as PILImage

from .exceptions import UploaderException
from .uploaded_file import UploadedFile
from .uploader import Uploader


class Image(Uploader):
    """Allow jpg, png and gif images. Resizes via Pillow (replaces PHP GD)."""

    _allow_types: ClassVar[list[str]] = [
        "image/jpeg",
        "image/png",
        "image/gif",
    ]

    _extensions: ClassVar[list[str]] = [
        "jpg",
        "jpeg",
        "png",
        "gif",
    ]

    def upload(
        self,
        image: UploadedFile,
        name: str,
        width: int = 2000,
        quality: Optional[dict[str, int]] = None,
    ) -> str:
        if not image.content_type:
            raise UploaderException("Not a valid data from image")

        if image.content_type not in self._allow_types:
            raise UploaderException("Not a valid image type or extension")

        # Internal canonical extension (jpeg → jpg)
        mime = image.content_type
        if mime == "image/jpeg":
            self.ext = "jpg"
        elif mime == "image/png":
            self.ext = "png"
        elif mime == "image/gif":
            self.ext = "gif"
        else:
            raise UploaderException("Not a valid image type or extension")

        self._name(name)
        dst = f"{self.path}/{self.name}"

        if self.ext == "gif":
            image.save_to(dst)
            return dst

        q = quality if quality is not None else {"jpg": 75, "png": 5}
        with image.open() as src:
            self.file = PILImage.open(src)
            self.file.load()
        self._image_generate(width, q, dst)
        return dst

    def _image_generate(self, width: int, quality: dict[str, int], dst_path: str) -> None:
        src: PILImage.Image = self.file
        file_x, file_y = src.size
        image_w = width if width < file_x else file_x
        image_h = int((image_w * file_y) / file_x)

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
