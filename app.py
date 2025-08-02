import requests
import json
import time
from datetime import datetime, timedelta
import os

API_URL = "https://bulk-indexer-6ezm.onrender.com/index"
LOG_FILE = "indexed.log"
ERR_FILE = "errors.log"
KEEP_DAYS = 7  # loglarda faqat oxirgi 7 kunni saqlash

def clean_old_logs(file_path):
    """Log fayldan faqat oxirgi 7 kunlik yozuvlarni qoldirish"""
    if not os.path.exists(file_path):
        return
    lines_to_keep = []
    cutoff_date = datetime.now() - timedelta(days=KEEP_DAYS)
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                timestamp_str = line.split(" - ")[0]
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                if timestamp >= cutoff_date:
                    lines_to_keep.append(line)
            except Exception:
                continue
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines_to_keep)

def get_already_indexed():
    """indexed.log ichidan allaqachon yuborilgan URL'larni olish"""
    if not os.path.exists(LOG_FILE):
        return set()
    urls = set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if "Indexed:" in line:
                url = line.strip().split("Indexed: ")[-1]
                urls.add(url)
    return urls

def log_success(urls):
    clean_old_logs(LOG_FILE)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for url in urls:
            f.write(f"{datetime.now()} - Indexed: {url}\n")

def log_error(urls, error_msg):
    clean_old_logs(ERR_FILE)
    with open(ERR_FILE, "a", encoding="utf-8") as f:
        for url in urls:
            f.write(f"{datetime.now()} - Error: {url} - {error_msg}\n")

def submit_urls():
    with open("urls.txt", "r", encoding="utf-8") as f:
        all_urls = [line.strip() for line in f if line.strip()]

    already_indexed = get_already_indexed()
    new_urls = [url for url in all_urls if url not in already_indexed]

    if not new_urls:
        print("⚡ Yangi URL yo'q, yuborilmaydi.")
        return

    batch_size = 100
    for i in range(0, len(new_urls), batch_size):
        batch = new_urls[i:i+batch_size]
        payload = {"urls": batch}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
            if response.status_code == 200:
                print("✅ Yuborildi:", batch)
                log_success(batch)
            else:
                print("❌ Xato:", response.text)
                log_error(batch, response.text)
        except Exception as e:
            print("❌ Ulanishda xato:", e)
            log_error(batch, str(e))

        time.sleep(2)  # quota limitiga tushib qolmaslik uchun

if __name__ == "__main__":
    submit_urls()
