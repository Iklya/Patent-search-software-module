FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV MODEL_PATH=app/ml_models/keyt5_patent
ENV MAX_INPUT_LENGTH=10000

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pytest app/tests

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]