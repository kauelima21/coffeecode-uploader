"""Exemplo Flask: envio de arquivo (equivalente a example/file.php)."""
from __future__ import annotations

from flask import Flask, request

from coffeecode_uploader import File, UploadedFile, UploaderException

app = Flask(__name__)
HTML = """
<!doctype html>
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
        try:
            upload = UploadedFile.from_flask(request.files["file"])
            f = File("uploads", "files")
            path = f.upload(upload, request.form["name"])
            result = f"<p><a href='/{path}' target='_blank'>@CoffeeCode</a></p>"
        except UploaderException as e:
            result = f"<p>(!) {e}</p>"
    return HTML.format(result=result)


if __name__ == "__main__":
    app.run(debug=True)
