"""Exemplo Flask: envio de midia (equivalente a example/media.php)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, request

from coffeecode_uploader import Media, UploaderException

app = Flask(__name__)
HTML = """
<!doctype html>
<form method="post" enctype="multipart/form-data">
  <input type="text" name="name" placeholder="File Name" required>
  <input type="file" name="file" required>
  <button>Send Media</button>
</form>
{result}
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST" and "file" in request.files:
        upload = request.files["file"]
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            upload.save(tmp.name)
            tmp_path = tmp.name
        try:
            m = Media("uploads", "medias")
            path = m.upload(
                {"name": upload.filename, "type": upload.mimetype, "tmp_name": tmp_path},
                request.form["name"],
            )
            result = f"<p><a href='/{path}' target='_blank'>@CoffeeCode</a></p>"
        except UploaderException as e:
            result = f"<p>(!) {e}</p>"
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    return HTML.format(result=result)


if __name__ == "__main__":
    app.run(debug=True)
