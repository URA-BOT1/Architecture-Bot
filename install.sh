#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils
pip install -r requirements.txt
pip install -r backend/requirements.txt
