from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os, json, requests, time
from bs4 import BeautifulSoup

app = Flask(__name__)

# Google API credentialsni Render Environment Variables dan yuklash
credentials_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
SCOPES = ['https://www.googleapis.com/auth/indexing']
credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
service = build('indexing', 'v3', credentials=credentials)

def check_canonical(url):
    """ Sahifadan canonical linkni topish """
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.get("href"):
            return canonical_tag["href"]
        return None
    except:
        return None

def index_url(url):
    canonical_found = check_canonical(url)
    if canonical_found and canonical_found.strip() != url.strip():
        note = f"⚠ Google chalkashishi mumkin. Canonical topildi: {canonical_found}"
    else:
        note = "✅ Canonical to'g'ri yoki yo'q"

    try:
        publish_request = {'url': url, 'type': 'URL_UPDATED'}
        service.urlNotifications().publish(body=publish_request).execute()
        return {"url": url, "status": "Indexed", "note": note}
    except Exception as e:
        return {"url": url, "status": "Error", "error": str(e), "note": note}

@app.route('/bulk', methods=['POST'])
def bulk_index():
    file = request.files['file']
    urls = file.read().decode('utf-8').splitlines()
    results = []
    for url in urls:
        if url.strip():
            results.append(index_url(url.strip()))
            time.sleep(2)  # API limitdan oshmaslik uchun
    return jsonify(results)

@app.route('/')
def home():
    return '''
    <h2>Google Bulk Indexer + Canonical Checker</h2>
    <form action="/bulk" method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv,.txt" required>
        <button type="submit">Indeksga yuborish</button>
    </form>
    '''

if __name__ == '__main__':
    # Render free plan PORT environment variable ishlatadi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
