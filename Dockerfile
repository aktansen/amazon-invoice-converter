FROM python:3.10-slim

# Tesseract ve gerekli bağımlılıkları yükle
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev poppler-utils && \
    apt-get clean

# Çalışma dizinine geç
WORKDIR /app

# Dosyaları kopyala
COPY . /app

# pip güncelle ve bağımlılıkları kur
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı başlat
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
