# OCR Project

A Flask-based OCR web application that extracts text from image files, applies post-processing corrections, and lets users export the cleaned result as `DOCX`, `PDF`, or `TXT`.

## Overview

This project combines multiple OCR and text-cleaning steps into a simple browser workflow:

- Upload an image containing text
- Preview the selected image
- Extract text from printed or handwritten content
- Review and manually edit the recognized text
- Download the final result in `DOCX`, `PDF`, or `TXT` format

The application uses:

- `Tesseract OCR` for printed text
- `EasyOCR` for handwritten text
- `OpenCV` for preprocessing
- `SymSpell` for spelling correction
- `python-docx` and `reportlab` for export generation

## Features

- Supports image uploads in `png`, `jpg`, `jpeg`, `bmp`, and `tiff`
- Automatically distinguishes printed text from handwriting using edge-density heuristics
- Applies different preprocessing pipelines for printed and handwritten inputs
- Performs line-wise spelling correction with SymSpell
- Applies custom word replacements for known OCR mistakes
- Preserves line-based output for easier review
- Exports corrected text to `DOCX`, `PDF`, and `TXT`
- Simple web UI built with Flask templates, HTML, CSS, and JavaScript

## How It Works

1. The user uploads an image from the browser UI.
2. The backend saves the image to the `uploads/` folder.
3. The app checks whether the content looks more like printed text or handwriting.
4. Printed text is preprocessed and passed to Tesseract.
5. Handwritten text is preprocessed and passed to EasyOCR.
6. The extracted text is cleaned with SymSpell and custom replacements.
7. The user reviews or edits the text in the browser.
8. The final text is generated as a downloadable `DOCX`, `PDF`, or `TXT` file in `output/`.

## Project Structure

```text
ocrproject/
├── app.py
├── requirements.txt
├── README.md
├── static/
│   ├── style.css
│   └── javas.js
├── templates/
│   └── index.html
├── symspell_data/
│   ├── frequency_dictionary_en_82_765.txt
│   └── frequency_bigramdictionary_en_243_342.txt
├── uploads/
├── output/
├── ip img/
└── EasyOCR/
```

## Tech Stack

- Python
- Flask
- OpenCV
- Tesseract OCR
- EasyOCR
- SymSpellPy
- NumPy
- python-docx
- reportlab

## Requirements

Before running the project, make sure you have:

- Python 3.10+
- Tesseract OCR installed locally
- Pip available for Python package installation

## Installation

1. Clone or download the project.
2. Create and activate a virtual environment.
3. Install Python dependencies.
4. Install Tesseract OCR on your system.
5. Update the Tesseract path in `app.py` if needed.

### Create a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Tesseract setup

The project currently uses this Windows-specific path inside `app.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

If Tesseract is installed in a different location, update that path before running the app.

## Run the Application

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## API Endpoints

### `GET /`

Loads the main web interface.

### `POST /process`

Accepts an uploaded image and returns extracted text.

Request:

- Form field: `file`

Response:

```json
{
  "text": "recognized text",
  "imagePath": "uploads/example.jpg"
}
```

### `POST /finalize`

Accepts reviewed text and generates the final file.

Request body:

```json
{
  "correctedText": "final edited text",
  "fileType": "docx"
}
```

Response:

```json
{
  "downloadUrl": "/output/final_output.docx"
}
```

### `GET /output/<filename>`

Downloads the generated output file.

## Main Implementation Notes

- `app.py` contains both the OCR pipeline and Flask routes.
- Printed text and handwriting use separate preprocessing logic.
- SymSpell dictionaries are loaded from `symspell_data/`.
- Output files are always written to the `output/` directory.
- Uploaded files are stored in the `uploads/` directory.

## Limitations

- The Tesseract path is hardcoded for Windows and should be made configurable for portability.
- The current OCR configuration is English-only.
- The printed-vs-handwritten detection uses a simple heuristic and may misclassify some images.
- Custom corrections are manually defined and currently cover only a small number of words.
- Output filenames are fixed as `final_output.<ext>`, so newer downloads overwrite older ones.
- The project currently includes many generated files and sample uploads inside the repository.

## Future Improvements

- Move the Tesseract path to an environment variable or config file
- Add support for multiple languages
- Improve handwriting detection accuracy
- Add unique filenames for generated outputs
- Separate frontend JavaScript into a single active script file
- Add tests for OCR routes and export generation
- Add Docker support for easier setup

## References

- Tesseract OCR
- EasyOCR
- SymSpellPy
- Flask
- OpenCV

## Author

Sanjana S Kadakabhavi

LinkedIn: https://linkedin.com/in/sanjana-kadakabhavi-8741bb25b
GitHub: https://github.com/Sanjanask13
