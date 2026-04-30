"""Exemplo Flask: envio de imagem (equivalente a example/image.php)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, request

from coffeecode_uploader import Image, UploaderException

app = Flask(__name__)
HTML = """
<!doctype html>
<form method="post" enctype="multipart/form-data">
  <input type="text" name="name" placeholder="Image Name" required>
  <input type="file" name="image" required>
  <button>Send Image</button>
</form>
{result}
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST" and "image" in request.files:
        upload = request.files["image"]
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            upload.save(tmp.name)
            tmp_path = tmp.name
        try:
            image = Image("uploads", "images")
            file_dict = {
                "name": upload.filename,
                "type": upload.mimetype,
                "tmp_name": tmp_path,
            }
            path = image.upload(file_dict, request.form["name"])
            result = f"<img src='/{path}' width='100%'>"
        except UploaderException as e:
            result = f"<p>(!) {e}</p>"
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    return HTML.format(result=result)


if __name__ == "__main__":
    app.run(debug=True)
