@echo off
REM Helper script to run app1 (localhost only)

echo Starting AI Sandbox - App1...
echo URL: http://localhost:8501
echo Press Ctrl+C to stop
echo.

python -m streamlit run streamlit_main.py --server.address=localhost --server.headless=true
