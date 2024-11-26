@echo off
echo 🚀 Starting Web2MD build process for Windows...

REM Check if conda is installed
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Conda is not installed. Please install Miniconda or Anaconda first.
    exit /b 1
)

REM Check if the environment exists and remove it if it does
conda env list | findstr /i "web2md_new" >nul
if %ERRORLEVEL% EQU 0 (
    echo 🔄 Removing existing conda environment...
    call conda env remove -n web2md_new -y
)

REM Create and activate conda environment
echo 🔧 Creating new conda environment...
call conda create -n web2md_new python=3.10 -y
call conda activate web2md_new

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Run the build script
echo 🏗️ Building the application...
python build.py

REM Check if build was successful
if exist "dist\Web2MD.exe" (
    echo ✅ Build successful! The application is in the dist directory.
    echo 📍 Location: %CD%\dist\Web2MD.exe
) else (
    echo ❌ Build failed. Please check the error messages above.
    exit /b 1
)

echo 🎉 Build process completed!
