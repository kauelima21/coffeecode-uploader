"""Exemplo Flask: envio de imagem (equivalente a example/image.php)."""
from __future__ import annotations

from flask import Flask, request

from coffeecode_uploader import Image, UploadedFile, UploaderException

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
        try:
            upload = UploadedFile.from_flask(request.files["image"])
            image = Image("uploads", "images")
            path = image.upload(upload, request.form["name"])
            result = f"<img src='/{path}' width='100%'>"
        except UploaderException as e:
            result = f"<p>(!) {e}</p>"
    return HTML.format(result=result)


if __name__ == "__main__":
    app.run(debug=True)
