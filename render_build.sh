#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- INSTALLING PYTHON DEPENDENCIES ---"
pip install --upgrade pip
pip install -r requirements.txt

echo "--- INSTALLING PLAYWRIGHT BROWSERS ---"
# This command is critical for PDF generation on Render
playwright install --with-deps chromium

echo "--- BUILD COMPLETE ---"
