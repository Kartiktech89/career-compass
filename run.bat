@echo off
cd /d "%~dp0"
if not exist models\placement_model.joblib python -m placementiq.model
python -m streamlit run app\app.py
