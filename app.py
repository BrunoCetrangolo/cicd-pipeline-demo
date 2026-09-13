"""
app.py

Esta app es intencionalmente trivial. El protagonista de este
repo no es el código de negocio, sino el pipeline de CI/CD
(ver .github/workflows/pipeline.yml y el README).
"""

from flask import Flask, jsonify

app = Flask(__name__)


def get_version() -> str:
    """Versión de la app. En un pipeline real, este valor
    se suele inyectar automáticamente desde un tag de git
    en el momento del build (ver el job 'build' del pipeline)."""
    import os
    return os.environ.get("APP_VERSION", "dev")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": get_version()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
