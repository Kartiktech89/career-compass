#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -f models/placement_model.joblib ] || python -m placementiq.model
python -m streamlit run app/app.py
