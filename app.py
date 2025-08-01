from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# 🔹 Google Search Console API uchun sozlamalar
# TOKEN olish uchun GSC API OAuth2 kerak bo‘ladi (keyinroq sozlash mumkin)
GSC_API_URL = "https://indexing.googleapis.com/v3/urlNotifications:publish"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  

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
    for url in urls:
        try:
            payload = {
                "url": url.strip(),
                "type": "URL_UPDATED"
            }
            headers = {"Content-Type": "application/json"}
            if GOOGLE_API_KEY:
                r = requests.post(GSC_API_URL,
                                  params={"key": GOOGLE_API_KEY},
                                  json=payload,
                                  headers=headers)
                if r.status_code == 200:
                    results.append({"url": url, "status": "✅ Indekslash so‘rovi yuborildi"})
                else:
                    results.append({"url": url, "status": f"❌ Xato: {r.text}"})
            else:
                results.append({"url": url, "status": "❌ GOOGLE_API_KEY topilmadi"})
        except Exception as e:
            results.append({"url": url, "status": f"❌ Xato: {e}"})
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
