#!/bin/bash
# Exemples concrets Git Flow pour Architecture-Bot
# À copier-coller dans votre terminal ou donner à GPT Codex

# ========================================
# 1. SETUP INITIAL (à faire une seule fois)
# ========================================

# Cloner le repo si pas déjà fait
git clone https://github.com/URA-BOT1/Architecture-Bot.git
cd Architecture-Bot

# Initialiser Git Flow
git flow init -d

# Créer le tag initial sur master
git checkout master
git tag -a 0.1 -m "Version initiale avant corrections"
git push origin master --tags

# ========================================
# 2. APPLIQUER LES CORRECTIONS ACTUELLES
# ========================================

# Créer une feature pour les corrections
git checkout develop
git flow feature start fix-critical-deployment-errors

# Appliquer toutes les corrections
echo "Applying fixes..."

# Fix 1: Dockerfile avec $PORT dynamique
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
EOF

git add backend/Dockerfile
git commit -m "fix(docker): configure dynamic PORT for Railway deployment

- Add PYTHONPATH environment variable
- Use shell form CMD for variable substitution
- Add Python optimization flags"

# Fix 2: Requirements sans fastapi-jwt-auth
# (copier le contenu du requirements.txt corrigé)
git add backend/requirements.txt
git commit -m "fix(deps): remove deprecated fastapi-jwt-auth

- Replace with python-jose for native JWT
- Update PyTorch to 2.2.0 to fix deprecation warnings
- Fix transformers compatibility"

# Fix 3: Railway configuration
cat > backend/railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 10,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF

git add backend/railway.json
git commit -m "feat(deploy): add Railway configuration with health checks"

# Terminer la feature
git flow feature finish fix-critical-deployment-errors

# ========================================
# 3. CRÉER UNE RELEASE 1.0
# ========================================

# Démarrer la release
git flow release start 1.0

# Mettre à jour la version
echo "1.0.0" > VERSION
echo "__version__ = '1.0.0'" > backend/__version__.py

git add VERSION backend/__version__.py
git commit -m "chore: bump version to 1.0.0"

# Mettre à jour le CHANGELOG
cat > CHANGELOG.md << 'EOF'
# Changelog

## [1.0.0] - 2024-12-20

### Fixed
- Railway deployment with dynamic $PORT configuration
- JWT authentication migration from deprecated library
- PyTorch deprecation warnings
- Docker module import errors with PYTHONPATH
- Redis connection pooling

### Added
- Railway deployment configuration
- Health check endpoint
- Lifespan pattern for FastAPI
- Comprehensive error handling

### Changed
- Migrated from fastapi-jwt-auth to python-jose
- Updated all dependencies to compatible versions
- Improved Docker build optimization

### Security
- Native JWT implementation with proper validation
- CORS configuration for production
EOF

git add CHANGELOG.md
git commit -m "docs: add changelog for version 1.0.0"

# Finaliser la release
git flow release finish -m "Release version 1.0.0" 1.0

# ========================================
# 4. POUSSER VERS GITHUB
# ========================================

# Pousser toutes les branches et tags
git push origin master develop --tags

# ========================================
# 5. DÉPLOYER SUR RAILWAY
# ========================================

# S'assurer d'être sur master pour le déploiement
git checkout master

# Déployer
railway up

# ========================================
# 6. CRÉER UNE NOUVELLE FEATURE
# ========================================

# Retour sur develop pour le développement
git checkout develop

# Exemple: Ajouter le support GPT-4
git flow feature start add-gpt4-support

# ... développement ...

# Exemple de commit
echo "GPT4_API_KEY=your-key" >> backend/.env.example
git add backend/.env.example
git commit -m "feat(llm): add GPT-4 API configuration"

# Terminer quand prêt
git flow feature finish add-gpt4-support

# ========================================
# 7. HOTFIX D'URGENCE
# ========================================

# Si bug critique en production
git flow hotfix start 1.0.1

# Corriger le bug
# Par exemple, fix du health check
sed -i 's/\/health/\/api\/health/g' backend/railway.json
git add backend/railway.json
git commit -m "fix(deploy): correct health check path in Railway config"

# Finaliser le hotfix
git flow hotfix finish -m "Hotfix version 1.0.1" 1.0.1

# Pousser le hotfix
git push origin master develop --tags

# ========================================
# 8. COMMANDES UTILES
# ========================================

# Voir l'état Git Flow
git flow config
git branch -a
git tag -l

# Lister les features actives
git flow feature list

# Nettoyer les branches locales mergées
git branch --merged | grep -v "\*\|master\|develop" | xargs -n 1 git branch -d

# Voir le graph complet
git log --graph --pretty=oneline --abbrev-commit --all

# ========================================
# 9. ALIASES PRATIQUES
# ========================================

# Configurer les aliases Git
git config --global alias.ffs "flow feature start"
git config --global alias.fff "flow feature finish"
git config --global alias.frs "flow release start"
git config --global alias.frf "flow release finish"
git config --global alias.fhs "flow hotfix start"
git config --global alias.fhf "flow hotfix finish"
git config --global alias.fl "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"

# Utilisation des aliases
git ffs my-feature  # Démarrer une feature
git fff my-feature  # Terminer une feature
git fl             # Voir le graph

# ========================================
# 10. INTÉGRATION CI/CD
# ========================================

# Créer GitHub Actions pour Git Flow
mkdir -p .github/workflows
cat > .github/workflows/gitflow.yml << 'EOF'
name: Git Flow CI/CD

on:
  push:
    branches: [ master, develop, 'release/**', 'hotfix/**' ]
  pull_request:
    branches: [ master, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd backend
          python test_corrections.py
          
  deploy:
    needs: test
    if: github.ref == 'refs/heads/master'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up
EOF

git add .github/workflows/gitflow.yml
git commit -m "ci: add GitHub Actions workflow for Git Flow"

echo "✅ Git Flow configuré avec succès pour Architecture-Bot!"