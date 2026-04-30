# Uploader (Python)

Port em Python do pacote PHP [coffeecode/uploader](https://github.com/robsonvleite/uploader)
de Robson V. Leite. Mantem o comportamento original (validacao por mime/extensao,
diretorios `YYYY/MM`, slug, redimensionamento de imagens) com uma API
**framework-agnostica** baseada em `UploadedFile` — aceita path em disco ou
stream em memoria, com adapters prontos para Flask e FastAPI.

> Python port of the PHP package [coffeecode/uploader](https://github.com/robsonvleite/uploader)
> by Robson V. Leite. Same behavior (mime/extension validation, year/month
> directories, slugged filenames, image resizing) with a framework-agnostic
> `UploadedFile` API: accepts a filesystem path or an in-memory stream, with
> built-in adapters for Flask and FastAPI.

## Destaques

- Upload simples de imagens, arquivos e midias
- `UploadedFile`: abstracao unica para path em disco ou stream
- Adapters: `from_flask`, `from_fastapi`, `from_stream`, `from_path`,
  `from_dict` (compat com PHP `$_FILES`)
- Gestao de diretorios com esquema de datas (`YYYY/MM`)
- Validacao por mime-type e extensao
- Redimensionamento e qualidade de imagem (substitui `ext-gd` por **Pillow**)

## Instalacao

```bash
pip install coffeecode-uploader
```

Requer Python >= 3.9 e Pillow >= 10.

## Uso

### Flask

```python
from flask import Flask, request
from coffeecode_uploader import Image, UploadedFile, UploaderException

@app.post("/avatar")
def avatar():
    try:
        upload = UploadedFile.from_flask(request.files["image"])
        path = Image("uploads", "images").upload(upload, request.form["name"])
        return {"path": path}
    except UploaderException as e:
        return {"error": str(e)}, 400
```

### FastAPI

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from coffeecode_uploader import Image, UploadedFile, UploaderException

app = FastAPI()

@app.post("/avatar")
async def avatar(name: str, image: UploadFile = File(...)):
    try:
        upload = UploadedFile.from_fastapi(image)
        path = Image("uploads", "images").upload(upload, name)
        return {"path": path}
    except UploaderException as e:
        raise HTTPException(400, str(e))
```

### Stream em memoria

```python
from io import BytesIO
from coffeecode_uploader import File, UploadedFile

upload = UploadedFile.from_stream(
    BytesIO(pdf_bytes),
    filename="report.pdf",
    content_type="application/pdf",
)
path = File("uploads", "files").upload(upload, "Relatorio Mensal")
```

### Path ja em disco

```python
from coffeecode_uploader import File, UploadedFile

upload = UploadedFile.from_path("/tmp/report.pdf", content_type="application/pdf")
path = File("uploads", "files").upload(upload, "Relatorio")
```

### Compat com `$_FILES` (PHP-style)

```python
from coffeecode_uploader import File, UploadedFile

upload = UploadedFile.from_dict({
    "name": "report.pdf",
    "type": "application/pdf",
    "tmp_name": "/tmp/upload.pdf",
})
path = File("uploads", "files").upload(upload, "Relatorio")
```

## API

### Construtores

```python
Image(upload_dir, file_type_dir, month_year_path=True)
File(upload_dir, file_type_dir, month_year_path=True)
Media(upload_dir, file_type_dir, month_year_path=True)
Send(upload_dir, file_type_dir, allow_types, extensions, month_year_path=True)
```

### `upload(file: UploadedFile, name: str, ...)`

Retorna a string com o caminho final relativo. Lanca `UploaderException`
quando o tipo MIME ou a extensao nao estao na lista permitida.

- `Image.upload(image, name, width=2000, quality=None)` — `quality` aceita
  `{"jpg": 0..95, "png": 0..9}`. Padrao: `{"jpg": 75, "png": 5}`. GIFs sao
  copiados sem reprocessamento (igual ao PHP).
- `File.upload(file, name)`
- `Media.upload(media, name)`
- `Send.upload(file, name)`

### `UploadedFile`

| Metodo                                      | Quando usar                                      |
|---------------------------------------------|--------------------------------------------------|
| `UploadedFile.from_flask(file_storage)`     | `request.files["x"]` em Flask/Quart              |
| `UploadedFile.from_fastapi(upload_file)`    | `UploadFile` em FastAPI/Starlette                |
| `UploadedFile.from_stream(stream, ...)`     | `BytesIO`, S3 body, qualquer file-like binario   |
| `UploadedFile.from_path(path, content_type)`| Arquivo ja em disco                              |
| `UploadedFile.from_dict({...})`             | Compat com `$_FILES` PHP                         |
| `.open()`                                   | Context manager → file-like binario              |
| `.save_to(dst)`                             | Copia para `dst` (preserva o source)             |
| `.extension`                                | Extensao em lowercase a partir de `filename`     |

### Helpers

- `Cls.is_allowed()` (alias `Cls.isAllowed()`) — lista de mime-types permitidos.
- `Cls.is_extension()` (alias `Cls.isExtension()`) — lista de extensoes permitidas.
- `Uploader.multiple([...])` — converte lista heterogenea (dict, FileStorage,
  UploadFile, UploadedFile) em `list[UploadedFile]`.

## Migrar de v1.x

A v1 aceitava um dict no formato PHP `$_FILES`. Em v2 use `UploadedFile`:

```python
# v1
file_dict = {"name": "x.pdf", "type": "application/pdf", "tmp_name": "/tmp/x"}
File("uploads", "files").upload(file_dict, "Doc")

# v2
upload = UploadedFile.from_dict(file_dict)
File("uploads", "files").upload(upload, "Doc")
```

## Equivalencia com a versao PHP

| PHP                                       | Python                                    |
|-------------------------------------------|-------------------------------------------|
| `CoffeeCode\Uploader\Image`               | `coffeecode_uploader.Image`               |
| `CoffeeCode\Uploader\File`                | `coffeecode_uploader.File`                |
| `CoffeeCode\Uploader\Media`               | `coffeecode_uploader.Media`               |
| `CoffeeCode\Uploader\Send`                | `coffeecode_uploader.Send`                |
| `Exception`                               | `UploaderException`                       |
| `$_FILES['x']`                            | `UploadedFile.from_dict({...})`           |
| `move_uploaded_file()`                    | `UploadedFile.save_to()`                  |
| `ext-gd`                                  | `Pillow`                                  |
| `monthYearPath`                           | `month_year_path`                         |

## Creditos

- API e comportamento original: Robson V. Leite — [coffeecode/uploader](https://github.com/robsonvleite/uploader) (MIT)
- Port Python: Kaue Leal

## Licenca

MIT.
