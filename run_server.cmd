@echo off
set PYTHONNOUSERSITE=1
python -m uvicorn app.main:app --reload
