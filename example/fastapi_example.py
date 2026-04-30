"""Exemplo FastAPI: envio de imagem usando UploadedFile.from_fastapi."""
from __future__ import annotations

from fastapi import FastAPI, File as FastAPIFile, HTTPException, UploadFile

from coffeecode_uploader import Image, UploadedFile, UploaderException

app = FastAPI()


@app.post("/upload-image")
async def upload_image(name: str, image: UploadFile = FastAPIFile(...)):
    try:
        upload = UploadedFile.from_fastapi(image)
        uploader = Image("uploads", "images")
        path = uploader.upload(upload, name)
        return {"path": path}
    except UploaderException as e:
        raise HTTPException(status_code=400, detail=str(e))
