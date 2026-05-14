from flask import Flask, request, jsonify, render_template, send_from_directory
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pytesseract
import cv2
import easyocr
import numpy as np
import os
import logging
from werkzeug.utils import secure_filename
import re
from symspellpy import SymSpell


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
dictionary_path = "symspell_data/frequency_dictionary_en_82_765.txt"
bigram_path = "symspell_data/frequency_bigramdictionary_en_243_342.txt"
sym_spell.load_dictionary(dictionary_path, 0, 1)
sym_spell.load_bigram_dictionary(bigram_path, 0, 2)


reader = easyocr.Reader(["en"], gpu=False)


app = Flask(__name__)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_custom_corrections(text):
    corrections = {
        "they": "the",
        "count": "sun"
    }
    for wrong, correct in corrections.items():
        text = re.sub(rf"\b{wrong}\b", correct, text, flags=re.IGNORECASE)
    return text

def correct_spelling(text):
    corrected_lines = []
    for line in text.splitlines():
        suggestions = sym_spell.lookup_compound(line, max_edit_distance=2)
        if suggestions:
            corrected_lines.append(suggestions[0].term)
        else:
            corrected_lines.append(line)
    return "\n".join(corrected_lines)


def is_printed_text(gray):
    # Canny edge detector to estimate edge density
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.mean(edges > 0)
    return edge_density > 0.08


def preprocess_printed(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    th = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 10
    )
    return th

def preprocess_handwriting(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=60)
    th = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        25, 15
    )
    th = cv2.medianBlur(th, 3)
    kernel = np.ones((3,3), np.uint8)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
    return th

def format_sentences_preserve(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_text_lines_tesseract(processed_img):
    data = pytesseract.image_to_data(
        processed_img,
        config="--oem 1 --psm 6",
        lang="eng",
        output_type=pytesseract.Output.DICT
    )
    lines = {}
    for i, text in enumerate(data["text"]):
        if text.strip():
            line_num = data["line_num"][i]
            if line_num not in lines:
                lines[line_num] = []
            lines[line_num].append(text)
    return "\n".join(" ".join(words) for words in lines.values())


def extract_text(image_path):
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if is_printed_text(gray):
            # Printed text → Tesseract
            processed = preprocess_printed(image_path)
            text = extract_text_lines_tesseract(processed)
        else:
            # Handwritten text → EasyOCR
            processed = preprocess_handwriting(image_path)
            text = "\n".join(reader.readtext(processed, detail=0, paragraph=True))
        
        text = correct_spelling(text)
        text = apply_custom_corrections(text)
        text = format_sentences_preserve(text)

        return text.strip()

    except Exception as e:
        logging.error(f"OCR error: {e}")
        return ""

def generate_word(text, output_path):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    doc.save(output_path)

def generate_pdf(text, output_path):
    pdf = canvas.Canvas(output_path, pagesize=letter)
    y = 750
    for line in text.splitlines():
        pdf.drawString(50, y, line)
        y -= 15
        if y < 50:
            pdf.showPage()
            y = 750
    pdf.save()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        text = extract_text(file_path)

        return jsonify({"text": text, "imagePath": file_path})

    except Exception as e:
        logging.error(f"Error in process_image: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/finalize", methods=["POST"])
def finalize():
    try:
        data = request.get_json()
        corrected_text = data.get("correctedText", "")
        file_type = data.get("fileType", "").lower()

        if not corrected_text or file_type not in {"docx", "pdf", "txt"}:
            return jsonify({"error": "Invalid input"}), 400

        filename = f"final_output.{file_type}"
        output_path = os.path.join(OUTPUT_DIR, filename)

        if file_type == "docx":
            generate_word(corrected_text, output_path)
        elif file_type == "pdf":
            generate_pdf(corrected_text, output_path)
        elif file_type == "txt":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(corrected_text)

        return jsonify({"downloadUrl": f"/output/{filename}"})

    except Exception as e:
        logging.error(f"Error in finalize: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/output/<filename>")
def serve_output(filename):
    try:
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
