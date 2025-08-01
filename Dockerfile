# Python image
FROM python:3.11-slim

# Ishchi papka
WORKDIR /app

# Talablarni o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini ko‘chirish
COPY . .

# Flask port
EXPOSE 5000

# Ishga tushirish
CMD ["python", "app.py"]
