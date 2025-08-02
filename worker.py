import time
from croniter import croniter
from datetime import datetime
import subprocess

# Cron ifodasi: har kuni soat 03:00 da
CRON_EXPRESSION = "0 3 * * *"

print("Worker ishga tushdi. Har kuni 03:00 da app.py bajariladi.")

while True:
    base_time = datetime.now()
    iter = croniter(CRON_EXPRESSION, base_time)
    next_run = iter.get_next(datetime)
    
    sleep_time = (next_run - base_time).total_seconds()
    print(f"Keyingi ishga tushirish: {next_run}, {sleep_time/60:.1f} daqiqadan so'ng")

    time.sleep(sleep_time)

    print("Boshlanmoqda...")
    subprocess.run(["python", "app.py"])
    print("Tugadi.")
