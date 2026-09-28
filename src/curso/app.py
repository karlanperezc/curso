from pathlib import Path

from flask import Flask

from curso.controllers.pdf_controller import pdf_bp
from curso.models import document_store

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["PDF_UPLOAD_DIR"] = PROJECT_ROOT / "PDF"
    app.config["DB_PATH"] = PROJECT_ROOT / "PDF" / "documents.db"
    document_store.init_db(app.config["DB_PATH"])
    app.register_blueprint(pdf_bp)
    return app
