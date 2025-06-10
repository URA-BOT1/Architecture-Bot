FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# IMPORTANT : Ajouter le répertoire au PYTHONPATH
ENV PYTHONPATH=/app
ENV PORT=8000

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Exposition du port
EXPOSE 8000

# Commande de démarrage
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
