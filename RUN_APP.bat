@echo off
cd /d "%~dp0"
python -m pip install -r requirements_cyber_rakshak_unified_v3.txt
python -m streamlit run cyber_rakshak_unified_v3.py
pause
