FROM python:3.10-slim

# Gerekli araçları ve Tesseract'ı yükle
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
        libleptonica-dev \
        poppler-utils \
        tesseract-ocr-eng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
