@echo off

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install requirements
pip install -r requirements.txt

REM Run the application
python main.py
