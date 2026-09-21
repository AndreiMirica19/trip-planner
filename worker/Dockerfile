FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home app
COPY --chown=app:app . .

USER app

CMD ["python", "worker.py"]