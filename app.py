from flask import Flask, request, jsonify, render_template
from googleapiclient.discovery import build
from google.oauth2 import service_account
from canonical_checker import check_canonical
import os, json, csv

app = Flask(__name__)

# Google API sozlamalari (Environment Variable orqali)
SCOPES = ["https://www.googleapis.com/auth/indexing"]
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)
service = build("indexing", "v3", credentials=credentials)

def publish_url(url):
    body = {
        "url": url,
        "type": "URL_UPDATED"
    }
    service.urlNotifications().publish(body=body).execute()

def read_urls_from_file(file_storage):
    """TXT yoki CSV dan URL ro'yxatini o'qish"""
    urls = []
    content = file_storage.read().decode("utf-8").strip()
    if file_storage.filename.endswith(".csv"):
        reader = csv.reader(content.splitlines())
        for row in reader:
            if row:
                urls.append(row[0].strip())
    else:  # txt
        for line in content.splitlines():
            if line.strip():
                urls.append(line.strip())
    return urls

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bulk_index_file", methods=["POST"])
def bulk_index_file():
    if "file" not in request.files:
        return jsonify({"error": "Fayl topilmadi"}), 400
    file = request.files["file"]
    urls = read_urls_from_file(file)
    results = []
    for url in urls:
        try:
            publish_url(url)
            results.append({"url": url, "status": "Indexed"})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return jsonify(results)

@app.route("/canonical_check_file", methods=["POST"])
def canonical_check_file():
    if "file" not in request.files:
        return jsonify({"error": "Fayl topilmadi"}), 400
    file = request.files["file"]
    urls = read_urls_from_file(file)
    results = [check_canonical(url) for url in urls]
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
