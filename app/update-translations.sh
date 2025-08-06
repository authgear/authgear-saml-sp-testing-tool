#!/bin/bash

# Script to compile translations and restart the Flask app
# Usage: ./update-translations.sh

set -e  # Exit on any error

echo "🔄 Compiling translations..."
source venv/bin/activate && pybabel compile -d translations

echo "🔄 Stopping Flask app..."
pkill -f "flask run" || true

echo "🚀 Starting Flask app..."
FLASK_APP=app ./venv/bin/flask run --host=0.0.0.0 --port=5001 --debug &

echo "✅ Translation update complete! App is running on http://localhost:5001" 