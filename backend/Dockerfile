dockerfileFROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# IMPORTANT : Ajouter le répertoire au PYTHONPATH
ENV PYTHONPATH=/app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Exposer le port
EXPOSE 8080

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
