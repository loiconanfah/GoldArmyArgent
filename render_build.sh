#!/usr/bin/env bash
# exit on error
set -o errexit

echo "--- INSTALLING PYTHON DEPENDENCIES ---"
pip install --upgrade pip
pip install -r requirements.txt

echo "--- INSTALLING PLAYWRIGHT BROWSERS ---"
# Force local install (to prevent Render from discarding cache between build and run)
export PLAYWRIGHT_BROWSERS_PATH="0"
# This command is critical for PDF generation on Render
playwright install chromium

echo "--- BUILD COMPLETE ---"
