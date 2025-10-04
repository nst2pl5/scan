@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting Flask server...
echo Server will be available at: http://localhost:5001
echo Press Ctrl+C to stop the server
flask --app app run --port=5001

