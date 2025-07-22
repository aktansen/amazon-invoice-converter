FROM python:3.10-slim

# Sistemde gerekli paketleri kur
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean

# Uygulama dosyalarını kopyala
WORKDIR /app
COPY . /app

# Bağımlılıkları yükle
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Sunucuyu başlat
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
