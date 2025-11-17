#!/bin/bash
set -e

echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..
echo "✅ Frontend build completed"

echo "📦 Installing dependencies from backend/requirements.txt..."
pip install -r backend/requirements.txt

echo "✅ Build completed successfully"
