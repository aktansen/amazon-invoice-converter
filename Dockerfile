FROM python:3.11-slim

# Sistemde tesseract kurulumu
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils

# Çalışma dizinini belirle
WORKDIR /app

# Gerekli dosyaları kopyala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uygulamayı başlat
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
