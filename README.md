# Real Estate & Notary Document Extractor (PoC)

A Proof of Concept (PoC) built with **Python** and **FastAPI** to automate the extraction, validation, and structuring of data from real estate deeds and notary certificates in batch, exporting clean results directly to **Excel (`.xlsx`)** spreadsheets.

---

## Key Features

* **Multimodal Batch Processing:** Supports simultaneous uploads of **native PDFs**, **scanned PDFs**, and **images (`.jpg`, `.jpeg`, `.png`)**.
* **Structured AI Extraction with Strict Schema:** Uses the **Google Gemini API** (`google-genai`) with `Pydantic` structured outputs and `temperature=0.0` to prevent hallucinations and enforce standardized fields (`Registry ID`, `Owner`, `Tax ID / CPF`, `Property Address`, `Transaction Value`, and `Liens/Encumbrances`).
* **3-Layer High-Availability Architecture (Multi-Provider + Offline Fallback):**
  1. **Primary Layer:** Google Gemini (`gemini-3.5-flash-lite` / `3.5-flash`) for fast multimodal extraction.
  2. **Secondary Fallback:** **Groq API** (`Llama 3.3 70B` & `Llama 4 Scout Vision`) triggered automatically upon external timeouts or `503/504` errors to prevent vendor lock-in and downtime.
  3. **Offline Contingency:** Local **Tesseract OCR** + **Regex** pipeline so operations continue uninterrupted even without internet access.
* **Deterministic Validation & Error Prevention:** Validates Brazilian Tax ID (`CPF`) formatting via Python post-extraction, automatically flagging inconsistent records (`Revisar Manualmente` / `REVISAR`) without halting batch execution.
* **Governance, Security & Data Privacy (LGPD / GDPR):**
  * Enterprise API usage without data retention for model training.
  * Automated audit trail (`auditoria.log`) recording timestamps, client IP, processed filenames, extracted registry IDs, and validation status.

---

## Tech Stack

* **Backend & Web UI:** Python 3.12, FastAPI, Uvicorn
* **AI & OCR:** Google GenAI SDK (`google-genai`), Groq SDK (`groq`), Tesseract OCR (`pytesseract`), Pillow, `pypdf`
* **Validation & Data Processing:** Pydantic, Pandas, OpenPyXL, Regex

---

## How to Run Locally

### 1. Prerequisites (Linux / Ubuntu / Mint)
Install the Tesseract OCR engine for offline image support:
```bash
sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-por
```
--- 

### 2. Clone the repository and set up the virtual environment

```bash
git clone [https://github.com/SEU-USUARIO/extrator-cartorio.git](https://github.com/SEU-USUARIO/extrator-cartorio.git)
cd extrator-cartorio

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
---

### 3. Configure environment variables

Crie um arquivo .env na raiz do projeto com a sua chave da API do Google AI Studio:
```bash
Snippet de código
GEMINI_API_KEY=sua_chave_aqui
```

---

### 4. Generate mock documents for testing (optional)

```bash
python gerar_pdfs_teste.py
```

---

### 5. Start the application

```bash
uvicorn main:app --reload
Open in your browser: http://127.0.0.1:8000
```