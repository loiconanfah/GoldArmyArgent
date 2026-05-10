#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- INSTALLING PYTHON DEPENDENCIES ---"
pip install --upgrade pip
pip install -r requirements.txt

echo "--- INSTALLING PLAYWRIGHT BROWSERS ---"
# Ensure we use the same path as in api/main.py (persistent directory on Render)
export PLAYWRIGHT_BROWSERS_PATH=$(pwd)/pw-browsers
# This command is critical for PDF generation on Render
playwright install chromium

echo "--- BUILD COMPLETE ---"
