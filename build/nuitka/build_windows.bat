@echo off
title GeoPandas Globe - Nuitka Build (Windows)

echo ========================================
echo 🚀 Building GeoPandas Globe with Nuitka
echo 🖥️ Windows Optimized Executable
echo ========================================
echo.

echo 📁 Navigating to application directory...
cd p3d
echo Current directory: %cd%

echo.
echo 🔍 Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    pause
    exit /b 1
)

echo ✅ Python available
echo.

echo 🧹 Cleaning previous builds...
if exist "globe_app.dist" rmdir /s /q "globe_app.dist"
if exist "globe_app.build" rmdir /s /q "globe_app.build"
if exist "globe_app.onefile-build" rmdir /s /q "globe_app.onefile-build"
if exist "GeoPandas-Globe-Nuitka.exe" del "GeoPandas-Globe-Nuitka.exe"

echo.
echo 🚀 Building with Nuitka (this may take 5-10 minutes)...
echo 💡 Nuitka compiles Python to C++ for better performance

nuitka ^
    --onefile ^
    --windows-console-mode=attach ^
    --include-data-dir=world_data=world_data ^
    --include-data-dir=gui=gui ^
    --include-data-dir=interfaces=interfaces ^
    --include-data-dir=settings=settings ^
    --follow-imports ^
    --output-filename=GeoPandas-Globe-Nuitka.exe ^
    globe_app.py

echo.
if %errorlevel% equ 0 (
    echo ✅ Build completed successfully!
    if exist "GeoPandas-Globe-Nuitka.exe" (
        echo 📁 Executable created: GeoPandas-Globe-Nuitka.exe
        dir GeoPandas-Globe-Nuitka.exe
        echo.
        echo 🚀 Testing the executable...
        GeoPandas-Globe-Nuitka.exe
    ) else (
        echo ❌ Executable not found
    )
) else (
    echo ❌ Build failed! Check output above for errors.
)

echo.
echo Press any key to continue...
pause > nul
