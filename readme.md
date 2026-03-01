# Healthcare Chatbot (Gradio)

A simple healthcare-themed chatbot built with **Gradio** and **Gemini**.

## What Changed

- Removed the RAG-based document retrieval flow from the primary app path.
- Added a lightweight chat interface focused on healthcare guidance.
- Updated the frontend styling to a healthcare visual theme.

## Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Configure environment

Create or update `.env`:

```env
GEMINI_API_KEY=your_api_key_here
DEFAULT_MODEL=gemini-2.5-flash
PORT=7860
```

### 3) Run the chatbot

```bash
python main.py
```

Then open: `http://127.0.0.1:7860`

## App Behavior

- The assistant is tuned for general health and wellness questions.
- It includes safety guidance and avoids definitive diagnosis.
- It is **not** a replacement for medical professionals.

## Main Files

- `app.py` — Gradio healthcare chatbot UI and Gemini response logic
- `main.py` — App launcher
- `frontend/index.html` — Healthcare-themed frontend page
- `requirements.txt` — Python dependencies
