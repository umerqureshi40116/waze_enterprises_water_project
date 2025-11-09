#!/bin/bash
set -e

echo "📦 Installing dependencies from backend/requirements.txt..."
pip install -r backend/requirements.txt

echo "✅ Build completed successfully"
