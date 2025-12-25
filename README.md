# 🚀 OptiResume – AI-Powered Resume Intelligence Platform

OptiResume is an end-to-end **AI-powered resume analysis and career assistance platform** that helps users understand, score, and improve their resumes for modern job markets.

Unlike traditional resume parsers or ATS checkers, OptiResume combines **document intelligence, structured extraction, scoring logic, and generative AI** to deliver actionable insights and personalized career tools.

---

## 🌟 Key Features

### 📄 Smart Resume Ingestion
- Upload resumes in **PDF, DOCX, or Image** formats
- Automatic text extraction using:
  - `pdfplumber` for native PDFs
  - OCR fallback with **Tesseract**
  - `python-docx` for DOCX files
- Handles real-world, unstructured resume layouts

---

### 🧠 AI-Based Resume Understanding
- Uses **Large Language Models (LLMs)** to convert raw resume text into structured JSON
- Extracts:
  - Personal & contact details
  - Skills (technical, tools, ML/AI, cloud, databases)
  - Experience with bullet points & metrics
  - Education, projects, certifications
- Output is **schema-validated with Pydantic** for reliability

---

### 📊 Resume Scoring Engine (UK-Focused)
- Rule-based + heuristic scoring logic
- Evaluates:
  - Contact completeness
  - Summary quality
  - Skills depth
  - Experience impact (metrics-aware)
  - Education & projects
- Produces:
  - Overall score (0–100)
  - Detailed breakdown
  - Human-readable reasons
  - Improvement recommendations

---

### ✨ AI Career Tools
Powered by reusable, versioned prompt templates:

- **Cover Letter Generator**
  - Tailored to resume + job description
  - UK-specific tone and structure

- **Mock Interview Questions**
  - Role-specific interview questions
  - Generated directly from resume & JD

- **Career Advice Assistant**
  - Free-form career guidance
  - Structured, actionable responses

---

### 👤 User System
- Secure signup & login
- Password hashing using **bcrypt**
- Session-based authentication
- User-isolated resume storage

---

### 🗄️ Persistent Storage
- MongoDB backend
- Stores:
  - Parsed resume data
  - Raw extracted text (safely capped)
  - Scores & metadata
- Repository pattern for clean data access

---

### 📈 Observability & Logging
- Structured **JSON logging**
- Request-level trace IDs
- Logs request lifecycle, AI latency, errors, and performance metrics
- Production-grade logging design

---

## 🧱 Architecture Overview

User Uploads Resume
↓
File Parser Layer
(PDF / DOCX / OCR)
↓
Raw Resume Text
↓
LLM Resume Extraction
(Structured JSON)
↓
Schema Validation
(Pydantic)
↓
Scoring Engine
(Rubric + Heuristics)
↓
MongoDB Storage
↓
AI Career Tools
(Cover Letter / Interview / Advice)

---

## 🛠️ Tech Stack

### Backend
- Python 3.9+
- FastAPI
- Jinja2
- MongoDB

### AI & NLP
- OpenAI API
- Prompt versioning system
- JSON-mode LLM outputs
- Retry + backoff + caching

### Parsing & OCR
- pdfplumber
- pytesseract
- Pillow
- python-docx

### Security
- passlib (bcrypt)
- Session middleware
- Environment-based config validation

---

## ⚡ Why OptiResume Is Different

| Area | Traditional Tools | OptiResume |
|---|---|---|
| Parsing | Keyword-based | AI + schema validation |
| Scoring | Static rules | Context-aware heuristics |
| Career Tools | Generic | Resume & role specific |
| Reliability | Fragile | Typed, logged, validated |
| Extensibility | Hard | Prompt & service based |

---

## 🚀 Getting Started

```bash
git clone https://github.com/amanramasharma/optiresume.git
cd optiresume

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn server.main:app --reload
