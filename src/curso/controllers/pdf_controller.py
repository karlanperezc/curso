from pathlib import Path

from flask import Blueprint, current_app, render_template, request
from werkzeug.utils import secure_filename

from curso.models.pdf_extractor import extract_text

pdf_bp = Blueprint("pdf", __name__)


@pdf_bp.route("/", methods=["GET", "POST"])
def index():
    extracted_text = None
    filename = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("pdf_file")

        if uploaded_file is None or uploaded_file.filename == "":
            error = "Selecciona un archivo PDF."
        elif not uploaded_file.filename.lower().endswith(".pdf"):
            error = "El archivo debe tener extensión .pdf."
        else:
            filename = secure_filename(uploaded_file.filename)
            upload_dir: Path = current_app.config["PDF_UPLOAD_DIR"]
            upload_dir.mkdir(parents=True, exist_ok=True)
            saved_path = upload_dir / filename
            uploaded_file.save(saved_path)
            extracted_text = extract_text(saved_path)

    return render_template(
        "index.html",
        extracted_text=extracted_text,
        filename=filename,
        error=error,
    )
