"""Exemplo Flask: envio generico (equivalente a example/send.php)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, request

from coffeecode_uploader import Send, UploaderException

app = Flask(__name__)
HTML = """
<!doctype html>
<p>Envie um arquivo AI (postscript)</p>
<form method="post" enctype="multipart/form-data">
  <input type="text" name="name" placeholder="File Name" required>
  <input type="file" name="file" required>
  <button>Send File</button>
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
            postscript = Send(
                "uploads",
                "postscript",
                allow_types=["application/postscript"],
                extensions=["ai"],
            )
            path = postscript.upload(
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
