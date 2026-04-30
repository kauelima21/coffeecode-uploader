# Uploader (Python)

Port em Python do pacote PHP [coffeecode/uploader](https://github.com/robsonvleite/uploader)
de Robson V. Leite. Mantem a mesma API e o mesmo comportamento: classes pequenas
para enviar imagens, arquivos e midias recebidos por um formulario, com gestao
de diretorios por ano/mes e validacao por mime-type/extensao.

> Python port of the PHP package [coffeecode/uploader](https://github.com/robsonvleite/uploader)
> by Robson V. Leite. It mirrors the original API and behavior: small classes
> to upload images, files and media from a form, with year/month directory
> management and mime-type/extension validation.

## Destaques

- Upload simples de imagens, arquivos e midias
- Gestao de diretorios com esquema de datas (`YYYY/MM`)
- Validacao por mime-type e extensao
- Redimensionamento e qualidade de imagem (substitui `ext-gd` por **Pillow**)
- API equivalente a do pacote PHP original

## Instalacao

```bash
pip install coffeecode-uploader
```

Requer Python >= 3.9 e Pillow >= 10.

## Uso

A entrada e um dicionario com as chaves `name`, `type` e `tmp_name` (mesmo
formato de `$_FILES` no PHP). Em frameworks como Flask ou FastAPI basta
montar esse dicionario a partir do arquivo recebido.

### Image

```python
from coffeecode_uploader import Image, UploaderException

image = Image("uploads", "images")            # com pastas ano/mes
# image = Image("uploads", "images", False)   # SEM pastas de ano e mes

try:
    file = {
        "name": request.files["image"].filename,
        "type": request.files["image"].mimetype,
        "tmp_name": "/tmp/upload.jpg",
    }
    path = image.upload(file, "Foto Perfil")        # width=2000, quality auto
    # path = image.upload(file, "Foto", 1280, {"jpg": 80, "png": 6})
except UploaderException as e:
    print(f"(!) {e}")
```

### File

```python
from coffeecode_uploader import File

f = File("uploads", "files")
path = f.upload(
    {"name": "report.pdf", "type": "application/pdf", "tmp_name": "/tmp/r.pdf"},
    "Relatorio Mensal",
)
```

### Media

```python
from coffeecode_uploader import Media

m = Media("uploads", "medias")
path = m.upload(
    {"name": "track.mp3", "type": "audio/mpeg", "tmp_name": "/tmp/t.mp3"},
    "Minha Musica",
)
```

### Send (tipos customizados)

```python
from coffeecode_uploader import Send

postscript = Send(
    "uploads",
    "postscript",
    allow_types=["application/postscript"],
    extensions=["ai"],
)
path = postscript.upload(file_dict, "Logo")
```

## API

### Construtor (todas as classes)

```python
Image(upload_dir, file_type_dir, month_year_path=True)
File(upload_dir, file_type_dir, month_year_path=True)
Media(upload_dir, file_type_dir, month_year_path=True)
Send(upload_dir, file_type_dir, allow_types, extensions, month_year_path=True)
```

### `upload(file_dict, name, ...)`

Retorna a string com o caminho final relativo. Lanca `UploaderException`
quando o tipo MIME ou a extensao nao estao na lista permitida.

- `Image.upload(image, name, width=2000, quality=None)` — `quality` aceita
  `{"jpg": 0..95, "png": 0..9}`. Padrao: `{"jpg": 75, "png": 5}`. GIFs sao
  copiados sem reprocessamento (igual ao PHP).
- `File.upload(file, name)`
- `Media.upload(media, name)`
- `Send.upload(file, name)`

### Helpers

- `Cls.is_allowed()` (alias `Cls.isAllowed()`) — lista de mime-types permitidos.
- `Cls.is_extension()` (alias `Cls.isExtension()`) — lista de extensoes permitidas.
- `instance.multiple(input_name, files)` — converte um envio multiplo no
  formato `$_FILES` em uma lista de dicionarios individuais.

## Comportamento de nome

O slug e gerado a partir de `name` com:

1. lowercase
2. normalizacao Unicode (NFKD) + remocao de acentos
3. caracteres nao alfanumericos viram `-`
4. extensao do arquivo original e anexada
5. se o arquivo final ja existir, `-{timestamp_unix}` e adicionado

## Equivalencia com a versao PHP

| PHP                                       | Python                                    |
|-------------------------------------------|-------------------------------------------|
| `CoffeeCode\Uploader\Image`               | `coffeecode_uploader.Image`               |
| `CoffeeCode\Uploader\File`                | `coffeecode_uploader.File`                |
| `CoffeeCode\Uploader\Media`               | `coffeecode_uploader.Media`               |
| `CoffeeCode\Uploader\Send`                | `coffeecode_uploader.Send`                |
| `Exception`                               | `UploaderException`                       |
| `$_FILES['x']`                            | `dict` com `name`, `type`, `tmp_name`     |
| `move_uploaded_file()`                    | `shutil.move` (com fallback `copyfile`)   |
| `ext-gd`                                  | `Pillow`                                  |
| `monthYearPath`                           | `month_year_path`                         |

## Creditos

- API e comportamento original: Robson V. Leite — [coffeecode/uploader](https://github.com/robsonvleite/uploader) (MIT)
- Port Python: Kaue Leal

## Licenca

MIT.
