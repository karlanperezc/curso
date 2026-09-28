from pathlib import Path

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from curso.models import document_store
from curso.models.pdf_extractor import extract_text

pdf_bp = Blueprint("pdf", __name__)


def _unique_filename(upload_dir: Path, filename: str) -> str:
    candidate = filename
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while (upload_dir / candidate).exists():
        candidate = f"{stem}-{counter}{suffix}"
        counter += 1
    return candidate


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
            upload_dir: Path = current_app.config["PDF_UPLOAD_DIR"]
            upload_dir.mkdir(parents=True, exist_ok=True)
            safe_name = secure_filename(uploaded_file.filename)
            filename = _unique_filename(upload_dir, safe_name)
            saved_path = upload_dir / filename
            uploaded_file.save(saved_path)
            extracted_text = extract_text(saved_path)

    db_path: Path = current_app.config["DB_PATH"]
    documents = document_store.list_documents(db_path)

    return render_template(
        "index.html",
        extracted_text=extracted_text,
        filename=filename,
        error=error,
        documents=documents,
    )


@pdf_bp.route("/save", methods=["POST"])
def save():
    filename = request.form.get("filename")
    upload_dir: Path = current_app.config["PDF_UPLOAD_DIR"]
    db_path: Path = current_app.config["DB_PATH"]

    if filename:
        saved_path = upload_dir / filename
        if saved_path.exists():
            text = extract_text(saved_path)
            document_store.save_document(db_path, filename, text)

    return redirect(url_for("pdf.index"))


@pdf_bp.route("/discard", methods=["POST"])
def discard():
    filename = request.form.get("filename")
    upload_dir: Path = current_app.config["PDF_UPLOAD_DIR"]

    if filename:
        (upload_dir / filename).unlink(missing_ok=True)

    return redirect(url_for("pdf.index"))


@pdf_bp.route("/documents/<int:doc_id>/delete", methods=["POST"])
def delete_document(doc_id: int):
    db_path: Path = current_app.config["DB_PATH"]
    upload_dir: Path = current_app.config["PDF_UPLOAD_DIR"]

    doc = document_store.get_document(db_path, doc_id)
    if doc:
        document_store.delete_document(db_path, doc_id)
        (upload_dir / doc["filename"]).unlink(missing_ok=True)

    return redirect(url_for("pdf.index"))
