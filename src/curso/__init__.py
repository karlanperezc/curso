from curso.app import create_app


def main() -> None:
    create_app().run(debug=True)
