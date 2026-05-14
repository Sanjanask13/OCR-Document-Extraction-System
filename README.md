# OCR Document Extraction System

## Overview
OCR Document Extraction System is an AI-powered web application that extracts text from images and scanned documents using Optical Character Recognition (OCR) techniques. The project combines image preprocessing, OCR extraction, and text correction to generate editable document outputs.

---

## Features
- Image upload support
- OCR-based text extraction
- Image preprocessing using OpenCV
- Text correction using SymSpell
- Export extracted text to editable formats
- User-friendly Flask web interface

---

## Technologies Used

### Backend
- Python
- Flask

### OCR & Image Processing
- EasyOCR
- Tesseract OCR
- OpenCV
- Pillow

### NLP & Text Correction
- SymSpellPy
- NLTK

### Document Generation
- python-docx
- ReportLab

---

## Project Structure

```bash
OCR-Document-Extraction-System/
│
├── app.py
├── README.md
├── requirements.txt
├── static/
├── templates/
├── symspell_data/
├── uploads/
└── output/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Sanjanask13/OCR-Document-Extraction-System.git
```

### Navigate to Project Folder

```bash
cd OCR-Document-Extraction-System
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

---

## How It Works

1. User uploads an image or scanned document
2. Image preprocessing is applied
3. OCR extracts text from image
4. SymSpell corrects extracted text
5. Output is generated in editable format

---

## Future Enhancements
- Better table extraction
- Layout preservation
- Multi-language OCR support
- AI-based document understanding
- Improved OCR accuracy

---

## Author
Sanjana Kadakabhavi
