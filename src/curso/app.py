from pathlib import Path

from flask import Flask

from curso.controllers.pdf_controller import pdf_bp

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["PDF_UPLOAD_DIR"] = PROJECT_ROOT / "PDF"
    app.register_blueprint(pdf_bp)
    return app
