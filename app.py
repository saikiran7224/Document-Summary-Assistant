# app.py
import streamlit as st
from io import BytesIO
import os

# Optional libs (pdf/image). If not installed, upload text or plain .txt
try:
    import pdfplumber
except Exception:
    pdfplumber = None
try:
    from PIL import Image
    import pytesseract
except Exception:
    Image = None
    pytesseract = None

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import math

# Ensure punkt is available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

st.set_page_config(page_title="Simple Document Summarizer", layout="centered")
st.title("📝 Simple Document Summarizer (No API key)")

st.markdown(
    "Upload a text file or PDF (text-based), paste/enter text, or upload an image (optional OCR). "
    "The app will extract text and produce an extractive summary (short/medium/long)."
)

col1, col2 = st.columns([3,1])

with col1:
    source = st.radio("Input source", ("Paste / Type text", "Upload file"), index=0)

with col2:
    length = st.selectbox("Summary length", ("Short", "Medium", "Long"))

text_input = ""
if source == "Paste / Type text":
    text_input = st.text_area("Paste your document text here", height=300)

else:
    uploaded = st.file_uploader("Upload .txt, .pdf (text), or image (png/jpg) — image OCR requires Tesseract installed", type=["txt","pdf","png","jpg","jpeg"])
    if uploaded:
        fname = uploaded.name.lower()
        if fname.endswith(".txt"):
            raw = uploaded.read()
            try:
                text_input = raw.decode("utf-8")
            except Exception:
                text_input = raw.decode("latin-1", errors="ignore")
        elif fname.endswith(".pdf"):
            if not pdfplumber:
                st.warning("PDF support requires pdfplumber. Install from requirements or use Paste text.")
            else:
                try:
                    with pdfplumber.open(BytesIO(uploaded.read())) as pdf:
                        pages = [p.extract_text() or "" for p in pdf.pages]
                        text_input = "\n".join(pages)
                except Exception as e:
                    st.error("Failed to read PDF: " + str(e))
        elif fname.endswith((".png",".jpg","jpeg")):
            if not (Image and pytesseract):
                st.warning("Image OCR requires pillow and pytesseract plus system Tesseract. You can paste text instead.")
            else:
                try:
                    img = Image.open(uploaded)
                    text_input = pytesseract.image_to_string(img)
                except Exception as e:
                    st.error("OCR failed: " + str(e))

if not text_input or text_input.strip() == "":
    st.info("No text available yet. Paste text, or upload a file (text/pdf/image).")
else:
    st.subheader("Preview (first 3000 chars)")
    st.write(text_input[:3000] + ("..." if len(text_input)>3000 else ""))

    # Summarizer functions
    def _clean_and_tokenize_words(txt):
        words = [w.lower() for w in word_tokenize(txt) if w.isalpha()]
        return words

    def _score_sentences(text):
        sentences = sent_tokenize(text)
        words = _clean_and_tokenize_words(text)
        if not words:
            return [(i,0.0,s) for i,s in enumerate(sentences)]
        freq = Counter(words)
        maxf = max(freq.values())
        for k in freq:
            freq[k] = freq[k] / maxf
        scored = []
        for i,s in enumerate(sentences):
            s_words = [w.lower() for w in word_tokenize(s) if w.isalpha()]
            if not s_words:
                score = 0.0
            else:
                score = sum(freq.get(w,0) for w in s_words) / len(s_words)
            scored.append((i, score, s))
        return scored

    def generate_summary(text, mode="Medium"):
        sentences = sent_tokenize(text)
        if len(sentences) <= 1:
            return text.strip()
        scored = _score_sentences(text)
        # choose number of sentences by mode
        if mode == "Short":
            k = max(1, math.ceil(len(sentences) * 0.08))  # ~8% of sentences
        elif mode == "Medium":
            k = max(1, math.ceil(len(sentences) * 0.18))  # ~18%
        else:
            k = max(1, math.ceil(len(sentences) * 0.35))  # ~35%
        top = sorted(scored, key=lambda x: x[1], reverse=True)[:k]
        top_sorted = sorted(top, key=lambda x: x[0])
        summary = " ".join([s for (_, _, s) in top_sorted])
        return summary

    # produce summary
    with st.spinner("Generating summary..."):
        summary_text = generate_summary(text_input, mode=length)

    st.subheader(f"{length} summary")
    st.write(summary_text)

    st.download_button("Download summary (TXT)", data=summary_text, file_name="summary.txt", mime="text/plain")

    # show key sentences
    if st.checkbox("Show top key sentences", value=True):
        scored = _score_sentences(text_input)
        top5 = sorted(scored, key=lambda x: x[1], reverse=True)[:5]
        st.subheader("Top key sentences")
        for i,(idx,score,sent) in enumerate(top5,1):
            st.markdown(f"{i}.** {sent}  \n_score: {score:.3f}_")