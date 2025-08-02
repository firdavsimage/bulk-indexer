import requests
import json
import time

API_URL = "https://bulk-indexer-6ezm.onrender.com/index"

def submit_urls():
    with open("urls.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    # 100 tadan ko'p bo'lsa bo'lib yuboramiz
    batch_size = 100
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        payload = {"urls": batch}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
            print("Yuborildi:", batch)
            print("Javob:", response.text)
        except Exception as e:
            print("Xato:", e)

        time.sleep(2)  # Google limitidan oshmaslik uchun

if __name__ == "__main__":
    submit_urls()
