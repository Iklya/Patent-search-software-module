FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV MODEL_PATH=app/ml_models/keyt5_patent
ENV MAX_INPUT_LENGTH=10000

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxshmfence1 \
    libgtk-3-0 \
    libglib2.0-0 \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxcursor1 \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY . .

RUN playwright install chromium

# RUN pytest app/tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]