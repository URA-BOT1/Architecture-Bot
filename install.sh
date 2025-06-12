#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

# Install Python requirements for tests and source modules
pip install -r requirements.txt
# Install backend dependencies (also used by src/)
pip install -r backend/requirements.txt
