@echo off
echo ========================================
echo    UNICCON LOAN APPROVAL BOT
echo ========================================
echo.

echo Step 1: Checking if Ollama is running...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Ollama is not running or not installed!
    echo.
    echo Please make sure:
    echo 1. Ollama is installed from https://ollama.ai/
    echo 2. Run: ollama pull llama2
    echo 3. Ollama service is running
    echo.
    pause
    exit /b 1
)
echo ✅ Ollama is running

echo.
echo Step 2: Checking if llama2 model is available...
ollama list | findstr "llama2" >nul
if %errorlevel% neq 0 (
    echo WARNING: llama2 model not found!
    echo Downloading llama2 model (this may take a few minutes)...
    ollama pull llama2
)
echo ✅ llama2 model is available

echo.
echo Step 3: Checking Python dependencies...
pip list | findstr "streamlit" >nul
if %errorlevel% neq 0 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)
echo ✅ Dependencies checked

echo.
echo Step 4: Checking for loan_data.csv...
if not exist "loan_data.csv" (
    echo ERROR: loan_data.csv not found in current directory!
    echo Please place your loan_data.csv file in the same folder as this script.
    echo.
    pause
    exit /b 1
)
echo ✅ loan_data.csv found

echo.
echo ========================================
echo    STARTING APPLICATION...
echo    Opening: http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C in this window to stop the application
echo.

timeout /t 3 /nobreak >nul

streamlit run app.py

pause