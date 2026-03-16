@echo off
setlocal EnableDelayedExpansion
REM start_all.bat — Start everything: database, API, and game
REM
REM Usage: start_all.bat [OPTIONS]
REM   -p, --panda3d    Launch Panda3D Desktop App
REM   -w, --web        Launch Web App (browser)
REM   -h, --help       Show this help message
REM
REM Without options, shows interactive menu.

set "SCRIPT_DIR=%~dp0"
set "FRONTEND_DIR=%SCRIPT_DIR%.."
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."
cd /d "%PROJECT_ROOT%"

REM Default values
set "FRONTEND="

REM Parse command line arguments
:parse_args
if "%~1"=="" goto done_args
if /i "%~1"=="-p" (
    set "FRONTEND=panda3d"
    shift
    goto parse_args
)
if /i "%~1"=="--panda3d" (
    set "FRONTEND=panda3d"
    shift
    goto parse_args
)
if /i "%~1"=="-w" (
    set "FRONTEND=web"
    shift
    goto parse_args
)
if /i "%~1"=="--web" (
    set "FRONTEND=web"
    shift
    goto parse_args
)
if /i "%~1"=="-h" goto show_help
if /i "%~1"=="--help" goto show_help
echo Unknown option: %~1
echo Use -h or --help for usage.
exit /b 1

:show_help
echo Usage: start_all.bat [OPTIONS]
echo.
echo Options:
echo   -p, --panda3d    Launch Panda3D Desktop App
echo   -w, --web        Launch Web App (browser)
echo   -h, --help       Show this help message
echo.
echo Without options, shows interactive menu.
exit /b 0

:done_args

echo.
echo 🌍 GeoChallenge Full Stack Launcher
echo ====================================

REM Show frontend menu if not specified via command line
if "%FRONTEND%"=="" (
    echo.
    echo Select frontend:
    echo   1) Panda3D Desktop App
    echo   2) Web App (browser)
    echo.
    set /p CHOICE="Enter choice [1-2]: "
    
    if "!CHOICE!"=="2" (
        set "FRONTEND=web"
    ) else (
        set "FRONTEND=panda3d"
    )
)

REM Handle choice from interactive mode
if "%CHOICE%"=="2" set "FRONTEND=web"
if "%CHOICE%"=="1" set "FRONTEND=panda3d"
if "%FRONTEND%"=="" set "FRONTEND=panda3d"

REM Start database
echo.
echo 📦 Starting database...
cd "%PROJECT_ROOT%\geochallenge-backend"
docker-compose up -d

REM Wait for database
echo ⏳ Waiting for database...
timeout /t 5 /nobreak >nul

REM Activate virtual environment
if exist "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
)

REM Install backend dependencies if needed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing backend dependencies...
    pip install -r requirements.txt
)

REM Start API in new window
echo 🚀 Starting API server...
start "GeoChallenge API" cmd /k "uvicorn api.main:app --host 0.0.0.0 --port 8000"
echo    API running at http://localhost:8000
timeout /t 3 /nobreak >nul

REM Start selected frontend
echo.
if "%FRONTEND%"=="web" (
    echo 🌐 Starting Web App...
    cd "%FRONTEND_DIR%\web"
    echo    Opening browser at http://localhost:8081
    start "GeoChallenge Web" cmd /c "python -m http.server 8081"
    timeout /t 2 /nobreak >nul
    start http://localhost:8081
    echo.
    echo Press any key to stop servers...
    pause >nul
    REM Stop web server
    taskkill /FI "WINDOWTITLE eq GeoChallenge Web*" >nul 2>&1
) else (
    echo 🎮 Starting Panda3D App...
    cd "%FRONTEND_DIR%\launch"
    call start_game.bat
)

REM Handle API shutdown
echo.
echo 🛑 Stopping API server...
taskkill /FI "WINDOWTITLE eq GeoChallenge API*" >nul 2>&1
echo Done!
