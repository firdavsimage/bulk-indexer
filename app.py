from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from google.oauth2 import service_account
from canonical_checker import check_canonical
import os
import json

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

@app.route("/bulk_index", methods=["POST"])
def bulk_index():
    data = request.json
    urls = data.get("urls", [])
    results = []
    for url in urls:
        try:
            publish_url(url)
            results.append({"url": url, "status": "Indexed"})
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return jsonify(results)

@app.route("/canonical_check", methods=["POST"])
def canonical_check():
    data = request.json
    urls = data.get("urls", [])
    results = [check_canonical(url) for url in urls]
    return jsonify(results)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "Google Bulk Indexer + Canonical Checker"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
