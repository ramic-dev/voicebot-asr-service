"""ASR Service — Whisper speech-to-text API."""

import os
import logging
import tempfile
from flask import Flask, request, jsonify

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__)

MODEL_SIZE = os.environ.get("WHISPER_MODEL", "small")
LANGUAGE = os.environ.get("LANGUAGE", "it")

log.info("Loading Whisper model '%s'...", MODEL_SIZE)
import whisper
model = whisper.load_model(MODEL_SIZE, device="cpu")
log.info("Whisper loaded.")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    tmp = tempfile.NamedTemporaryFile(suffix=".ogg", delete=False)
    audio.save(tmp.name)
    tmp.close()

    try:
        result = model.transcribe(tmp.name, language=LANGUAGE)
        text = result["text"].strip()
        log.info("Transcribed: %s", text[:100])
        return jsonify({"text": text})
    except Exception as e:
        log.error("Transcription failed: %s", e)
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp.name)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL_SIZE})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)
