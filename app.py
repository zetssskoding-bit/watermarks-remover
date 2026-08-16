import os
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request


# =========================
# Import Watermarks Remover
# =========================

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "service" / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

from text_unicode import clean_text


# =========================
# Flask App
# =========================

app = Flask(__name__)

MAX_CHARS = 200_000


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "service": "text-watermark-cleaner"
    })


@app.post("/api/clean")
def clean():
    data = request.get_json(silent=True) or {}

    text = data.get("text", "")

    if not isinstance(text, str):
        return jsonify({
            "ok": False,
            "error": "Text tidak valid."
        }), 400

    if not text:
        return jsonify({
            "ok": False,
            "error": "Masukkan teks terlebih dahulu."
        }), 400

    if len(text) > MAX_CHARS:
        return jsonify({
            "ok": False,
            "error": f"Maksimal {MAX_CHARS:,} karakter."
        }), 413

    try:
        cleaned, stats = clean_text(
            text,
            nfkc=False,
            aggressive_homoglyphs=False,
            normalize_spaces=True,
            strip_emoji_glue=False,
            strip_bidi=False,
        )

        return jsonify({
            "ok": True,
            "cleaned": cleaned,
            "stats": stats
        })

    except Exception as e:
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
