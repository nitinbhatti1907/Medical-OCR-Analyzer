# Medical OCR Analyzer

🔗 **Live Demo:** https://medical-ocr-analyzer.onrender.com  
Try it with a sample medical bill or prescription image and see the OCR + AI summary in action.

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [High Level Architecture](#high-level-architecture)
- [Tech Stack](#tech-stack)
- [Getting Started (Local Development)](#getting-started-local-development)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Create and activate virtual environment](#2-create-and-activate-virtual-environment)
  - [3. Install dependencies](#3-install-dependencies)
  - [4. Configure environment variables](#4-configure-environment-variables)
  - [5. Run migrations](#5-run-migrations)
  - [6. Start the development server](#6-start-the-development-server)
- [Setting up Azure AI Document Intelligence](#setting-up-azure-ai-document-intelligence)
- [Setting up Groq AI API](#setting-up-groq-ai-api)
- [How the Application Works](#how-the-application-works)
- [User Interface Overview](#user-interface-overview)
- [Deployment Notes (Render)](#deployment-notes-render)
- [Project Structure](#project-structure)
- [Limitations](#limitations)
- [Possible Future Improvements](#possible-future-improvements)
- [Credits](#credits)
- [License](#license)

---

## About the Project

**Medical OCR Analyzer** is a small end-to-end web application built for a Cloud Computing course project.  
The goal is to show how cloud services and AI models can work together to extract structured information from unstructured medical documents.

Typical use case:

- A user uploads an image of a **medical bill** or **prescription**.
- The app uses **Azure AI Document Intelligence** (OCR) to read all the text and return JSON.
- The JSON is passed to a **Groq-hosted Llama 3** model which summarizes and maps the text into a clean **key -> value** table (Patient Name, Doctor Name, Diagnosis, Medicines, Dates, etc).
- The UI displays both:
  - Raw OCR JSON (with a toggle)
  - A structured summary table that is easier to read and copy.

This is a **demo/academic project** only - not a production medical system.

---

## Key Features

- 📷 **Image upload** for PNG/JPG medical documents.
- 🔍 **Cloud OCR (Azure)** to extract text into JSON format.
- 🤖 **AI summarization (Groq Llama 3)** to convert OCR JSON into human friendly fields.
- 🧾 **Structured key -> value table** for quick scanning and copying.
- 🧱 **Collapsible JSON panel** so raw payload can be inspected when needed.
- 🎨 **Clean Tailwind CSS UI** with a single-page layout optimized for demos.
- 🌐 **Deployed on Render** using Gunicorn + WhiteNoise.

---

## High Level Architecture

Simple request flow:

1. User opens the website and uploads an image.
2. Django backend sends the image to **Azure AI Document Intelligence** using the prebuilt `read` model.
3. Azure returns OCR results as JSON (pages -> lines -> content).
4. Django constructs a compact JSON and sends it to a **Groq** Llama 3 chat completion with a custom prompt.
5. The AI model returns a text summary in lines like `Key: Value`.
6. Django parses this summary and renders it as an HTML table.
7. Front end shows:
   - Toggleable JSON box.
   - Scrollable structured summary table.

So basically:  
`Image -> Azure OCR -> JSON -> Groq LLM -> key/value table -> browser`.

---

## Tech Stack

**Backend**

- Python 3.11.x
- Django 5.x
- Azure AI Document Intelligence SDK (`azure-ai-formrecognizer`)
- Groq Python SDK (`groq`)
- Gunicorn (for production server on Render)
- WhiteNoise (for static file serving)

**Frontend**

- Django templates
- Tailwind CSS (via CDN)
- Vanilla JavaScript for:
  - Copy to clipboard
  - Toggle JSON panel

**Infra / Deployment**

- Azure AI services (Document Intelligence)
- Groq Cloud for Llama 3 model
- Render free tier for hosting the Django app

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.11.x installed
- Git installed
- Azure subscription (Azure for Students is fine)
- Groq account + API key

> The steps below assume you are in the **project root** (where `manage.py` lives).

### 1. Clone the repository

```bash
git clone https://github.com/nitinbhatti1907/Medical-OCR-Analyzer.git
cd Medical-OCR-Analyzer
```

### 2. Create and activate virtual environment

Windows (PowerShell):

```bash
python -m venv venv
.env\Scriptsctivate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root (same folder as `manage.py`):

```env
SECRET_KEY=your-long-django-secret-key
DEBUG=True

AZURE_FORMRECOGNIZER_ENDPOINT=https://your-azure-resource-name.cognitiveservices.azure.com/
AZURE_FORMRECOGNIZER_KEY=your-azure-formrecognizer-key

GROQ_API_KEY=your-groq-api-key
```

Notes:

- `SECRET_KEY` can be taken from your local `settings.py` or generated via `get_random_secret_key`.
- Never commit `.env` to GitHub (it is already in `.gitignore`).

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.  
You should see the **Medical OCR Analyzer** UI. Upload an image and test the flow.

---

## Setting up Azure AI Document Intelligence

Short version of the portal steps:

1. Sign in to the Azure Portal -> https://portal.azure.com
2. Make sure your subscription (eg. **Azure for Students**) is active.
3. Create a **Resource Group** (for example `rg-medical-ocr`).
4. Search for **Document Intelligence** (formerly Form Recognizer) -> click **Create**.
5. Configure:
   - Subscription -> your subscription
   - Resource Group -> `rg-medical-ocr`
   - Region -> eg. `Canada Central` or nearest region
   - Name -> eg. `cc-medical-ocr`
   - Pricing tier -> `F0` (free tier)
6. Wait for deployment to finish.
7. Open the resource -> go to **Keys and Endpoint**.
8. Copy:
   - **Endpoint** (something like `https://cc-medical-ocr.cognitiveservices.azure.com/`)
   - **Key 1** (or Key 2)

Add these to your `.env`:

```env
AZURE_FORMRECOGNIZER_ENDPOINT=your-endpoint-here
AZURE_FORMRECOGNIZER_KEY=your-key-here
```

---

## Setting up Groq AI API

1. Go to the Groq console -> https://console.groq.com
2. Create an account and generate an **API key**.
3. In your `.env`:

```env
GROQ_API_KEY=your-groq-api-key
```

4. In the code (Django view), the Groq client is initialized using this environment variable and calls a Llama 3 chat model to generate the structured summary.

---

## How the Application Works

Core logic is inside `core/views.py`:

- `analyze_image(image_file)`  
  -> Creates a `DocumentAnalysisClient` with Azure endpoint + key  
  -> Calls `begin_analyze_document("prebuilt-read", image_file)`  
  -> Returns a simplified JSON with pages and lines.

- `summarize_with_chatgpt(json_data)`  
  -> Builds a prompt that says: you are a medical data summarizer, here is JSON, map values into key: value lines.  
  -> Sends the prompt and JSON to Groq (Llama 3 model).  
  -> Returns the generated multi line summary string.

- `generate_html_table(prettified_result)`  
  -> Splits the summary into lines.  
  -> For any line containing `:` it splits into `key` and `value`.  
  -> Returns HTML `<tr><td>key</td><td>value</td></tr>` rows.

- `index(request)` view  
  -> On GET: just renders the page.  
  -> On POST: reads uploaded image, runs OCR + AI summarization + table generation and sends all results to the template.

---

## User Interface Overview

The main template lives at:  
`core/templates/core/index.html`

Key UI elements:

- Header with project title **Medical OCR Analyzer** and a small gradient card that hints at Health + AI.
- **Upload card** (centered):
  - File input for the image.
  - `Analyze` button.
  - Note about supported formats and that it is for CC project demonstration.
- **OCR JSON Result** panel:
  - Small `Toggle` button with arrow to show/hide raw JSON.
  - `Copy` button to copy the entire JSON payload.
- **Structured Summary (Key-Value)** panel:
  - Scrollable table with columns `Key` and `Value`.
  - `Copy` button to copy the raw text of the table.
- Layout is built with Tailwind classes and a single central column (`max-w-5xl`) so everything looks aligned and not too wide on large monitors.

---

## Deployment Notes (Render)

The project is deployed on **Render** using:

- `gunicorn ocr_project.wsgi:application --preload --timeout 600` as the start command
- `whitenoise` for static files (`STATIC_ROOT = staticfiles/`)
- Environment variables configured in Render dashboard:

  ```text
  SECRET_KEY
  DEBUG=False

  AZURE_FORMRECOGNIZER_ENDPOINT
  AZURE_FORMRECOGNIZER_KEY
  GROQ_API_KEY
  PYTHON_VERSION=3.11.6
  ```

ALLOWED_HOSTS in `ocr_project/settings.py` includes:

```python
ALLOWED_HOSTS = [
    "medical-ocr-analyzer.onrender.com",
    "localhost",
    "127.0.0.1",
]
```

Every git push to the `main` branch on GitHub can trigger a new deployment on Render (depending on your Render settings).

---

## Project Structure

Rough structure of the repository:

```text
Medical-OCR-Analyzer/
├─ core/
│  ├─ migrations/
│  ├─ templates/
│  │  └─ core/
│  │     └─ index.html        # Main UI template
│  ├─ views.py                # OCR + Groq logic
│  ├─ urls.py
│  └─ models.py               # (not heavily used in this prototype)
├─ ocr_project/
│  ├─ __init__.py
│  ├─ settings.py             # Django settings (env based)
│  ├─ urls.py                 # Root URL config
│  └─ wsgi.py                 # WSGI entry point for Gunicorn
├─ staticfiles/               # Collected static files (created in deploy)
├─ db.sqlite3                 # Local dev database
├─ manage.py
├─ requirements.txt
├─ .env                       # Local secrets (ignored in git)
├─ .gitignore
└─ README.md
```

---

## Limitations

- OCR accuracy depends heavily on input image quality (blur, rotation, handwriting etc).
- Groq Llama 3 model might sometimes:
  - Miss fields.
  - Over-guess or hallucinate values when the text is unclear.
- No authentication or user management - everything is anonymous.
- Data is not persisted in a database in a structured way for later analytics (demo only).
- Privacy and compliance (HIPAA, PHIPA etc) are **not** addressed. This is purely a student demo and should not be used for real patient data.

---

## Possible Future Improvements

Some ideas to extend the project later:

- Add user login and store extracted records securely in a database.
- Support export to CSV or PDF for the structured summary.
- Add a simple dashboard to aggregate costs, medicine frequency, or visit dates.
- Improve prompt engineering or use a smaller, fine-tuned medical model to reduce hallucinations.
- Add support for multiple languages or multi page PDFs.
- Add rate limiting and better error handling for production-like usage.

---

## Credits

- Built as part of a **Cloud Computing** course project.
- OCR powered by **Microsoft Azure AI Document Intelligence**.
- Summarization powered by **Groq** (Llama 3 model).
- Frontend styling with **Tailwind CSS**.

---

## License

This repository is intended primarily for learning and academic demonstration.  
You may reuse or modify the code at your own risk. If you adapt it, please keep appropriate credits for the original idea and cloud service providers.
