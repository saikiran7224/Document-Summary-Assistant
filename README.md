# 📄 Simple Document Summarizer (No API Key)

A lightweight, single-file Streamlit application that extracts text from documents and generates summaries locally — no API key, no cloud services, no heavy ML models required.

This project works with:

Pasted text

.txt files

Text-based PDF files

Images (.png/.jpg/.jpeg) → (optional OCR using Tesseract)

Summaries are generated using a clean, fast, extractive technique based on word frequency.

### 🚀 Features

✔ No API keys required — everything runs offline
✔ Single file app (app.py) for simplicity
✔ Upload: .txt, .pdf, .png, .jpg, .jpeg
✔ Optional OCR using Tesseract
✔ Three summary lengths: Short / Medium / Long
✔ Preview extracted text
✔ Download summary as .txt
✔ Show top key sentences

### 📂 Project Structure
project-folder/
│── app.py
│── requirements.txt
│── README.md
└── (optional) .venv/
