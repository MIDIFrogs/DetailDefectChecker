from flask import Flask, request, jsonify, send_file
import os
from typing import List, Dict
from PIL import Image
from detections_service import process_image
from image_service import save_image
from flask_cors import CORS

app = Flask(__name__)

# Folder to store processed images
PROCESSED_IMAGES_DIR = "runtime/processed"
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

@app.route("/api/process", methods=["POST"])
def process():
    image_file = request.files.get("image")
    if not image_file:
        return jsonify({"error": "No image file provided"}), 400

    scale_x = request.form.get("scale_x", 0.01, type=float)
    scale_y = request.form.get("scale_y", 0.01, type=float)

    image = Image.open(image_file)
    image_id = save_image(image, PROCESSED_IMAGES_DIR)
    result = process_image(image, scale_x, scale_y)
    result["downloadId"] = image_id
    return jsonify(result)

@app.route("/api/download/<int:id>", methods=["GET"])
def download(id: int):
    image_file = f"{PROCESSED_IMAGES_DIR}/{id}.png"
    return send_file(image_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
    CORS(app)
