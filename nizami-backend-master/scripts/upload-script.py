import os
import time

import requests

# === Configuration ===
FOLDER_PATH = os.path.expanduser("~/ref-docs")  # Change this to your target folder
# API_URL = "http://localhost:8000/api/v1/admin/reference-documents/"
API_URL = "https://api.app.nizami.ai/api/v1/admin/reference-documents/"
BEARER_TOKEN = ""
SLEEP_TIME = 0.2  # seconds between requests (set to 1 for 1-second delay)


# === Function to upload a docx file ===
def upload_docx(file_path: str, relative_name: str):
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    with open(file_path, "rb") as f:
        files = {
            "file": (relative_name, f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "name": relative_name,
            "language": "ar"
        }

        response = requests.post(API_URL, headers=headers, data=data, files=files)

    return response


# === Walk through folder and upload docx files ===
for root, dirs, files in os.walk(FOLDER_PATH):
    for file in files:
        if file.lower().endswith(".docx"):
            file_path = os.path.join(root, file)
            relative_name = os.path.relpath(file_path, FOLDER_PATH)

            print(f"Uploading: {file_path}")
            resp = upload_docx(file_path, relative_name)
            if resp.status_code in (200, 201):
                print(f"✅ Uploaded successfully: {file}")
            elif resp.status_code in (400, ):
                pass
            else:
                print(f"❌ Failed to upload {file}: {resp.status_code} - {resp.text}")
            time.sleep(SLEEP_TIME)
