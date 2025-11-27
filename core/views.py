from django.shortcuts import render
from django.http import JsonResponse
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import json
import os
from groq import Groq
import io

# Read keys from .env (via settings.py -> load_dotenv)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
AZURE_KEY = os.environ.get("AZURE_FORMRECOGNIZER_KEY", "")
AZURE_ENDPOINT = os.environ.get("AZURE_FORMRECOGNIZER_ENDPOINT", "")

# Groq client
groq_client = Groq(api_key=GROQ_API_KEY)


def analyze_image(image_file):
    client = DocumentAnalysisClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY)
    )
    poller = client.begin_analyze_document("prebuilt-read", image_file)
    result = poller.result()

    json_output = {"pages": []}
    for page in result.pages:
        page_data = {
            "page_number": page.page_number,
            "lines": [{"text": line.content} for line in page.lines]
        }
        json_output["pages"].append(page_data)

    return json.dumps(json_output, indent=2)


def summarize_with_chatgpt(json_data):
    prompt = (
        "You are a medical data summarizer. You will receive JSON data extracted from OCR scans of medical bills "
        "and prescriptions. Your task is to summarize this data without losing any information. "
        "Follow these instructions precisely:\n\n"
        "1. List every value found in the JSON data without using markdown.\n"
        "2. If a key is not recognized or not available, print the value directly; otherwise match with a key such as "
        "Doctor Name: xyz, Patient Name: abc and so on.\n"
        "3. Ensure that every piece of information from the JSON data is included in the summary.\n"
        "4. Preserve the order of the data as it appears in the JSON.\n"
        "5. Handle the data confidentially and ensure that no information is omitted.\n\n"
        "Here is the JSON data:\n\n"
        f"{json.dumps(json_data, indent=2)}"
    )

    completion = groq_client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.2,
    )

    return completion.choices[0].message.content.strip()


def generate_html_table(prettified_result):
    lines = prettified_result.strip().split('\n')
    html_rows = []
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            html_rows.append(f'<tr><td>{key}</td><td>{value}</td></tr>')
    html_table_rows = ''.join(html_rows)
    return html_table_rows


def index(request):
    result = None
    prettified_result = None
    final_result = None

    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image'].file
        result = analyze_image(image_file)
        json_data = json.loads(result)
        prettified_result = summarize_with_chatgpt(json_data)
        final_result = generate_html_table(prettified_result)

    return render(request, 'core/index.html', {
        'result': result,
        'prettified_result': final_result
    })