FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose un port par défaut (facultatif, ne sert qu'à documentation)
EXPOSE 8000

# CMD en mode shell pour permettre l'expansion des variables d'env
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
