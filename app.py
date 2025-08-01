from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import os, json
from google.auth.transport.requests import Request
from google.oauth2 import service_account

app = Flask(__name__)

# 🔹 Google Indexing API URL
GSC_API_URL = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# 🔹 Service Account JSON ni environmentdan olish
service_account_info = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}"))

credentials = None
if service_account_info:
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/indexing"]
    )

def get_access_token():
    """Access token olish"""
    global credentials
    if credentials and credentials.expired:
        credentials.refresh(Request())
    return credentials.token if credentials else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/canonical-check", methods=["POST"])
def canonical_check():
    urls = request.form.get("urls", "").splitlines()
    results = []
    for url in urls:
        try:
            r = requests.get(url.strip(), timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            canonical = soup.find("link", rel="canonical")
            canonical_url = canonical["href"] if canonical else "Yo‘q"
            results.append({
                "url": url,
                "canonical": canonical_url,
                "status": "✅ Mos" if canonical_url == url.strip() else "❌ Mos emas"
            })
        except Exception as e:
            results.append({"url": url, "canonical": "Xato", "status": str(e)})
    return jsonify(results)

@app.route("/bulk-index", methods=["POST"])
def bulk_index():
    urls = request.form.get("urls", "").splitlines()
    results = []

    token = get_access_token()
    if not token:
        return jsonify({"error": "❌ Access token olinmadi. JSON sozlamasini tekshiring."}), 400

    for url in urls:
        try:
            payload = {
                "url": url.strip(),
                "type": "URL_UPDATED"
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            r = requests.post(GSC_API_URL, json=payload, headers=headers)

            if r.status_code == 200:
                results.append({"url": url, "status": "✅ Indekslash so‘rovi yuborildi"})
            else:
                results.append({"url": url, "status": f"❌ Xato: {r.text}"})
        except Exception as e:
            results.append({"url": url, "status": f"❌ Xato: {e}"})
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
