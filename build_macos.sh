#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Web2MD build process for macOS..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

# Check if the environment exists and remove it if it does
if conda env list | grep -q "web2md_new"; then
    echo "🔄 Removing existing conda environment..."
    conda env remove -n web2md_new -y
fi

# Create and activate conda environment
echo "🔧 Creating new conda environment..."
conda create -n web2md_new python=3.10 -y
eval "$(conda shell.bash hook)"
conda activate web2md_new

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run the build script
echo "🏗️ Building the application..."
python build.py

# Check if build was successful
if [ -f "dist/Web2MD" ]; then
    echo "✅ Build successful! The application is in the dist directory."
    echo "📍 Location: $(pwd)/dist/Web2MD"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

# Create a DMG (optional)
if command -v create-dmg &> /dev/null; then
    echo "📀 Creating DMG installer..."
    create-dmg \
        --volname "Web2MD Installer" \
        --volicon "resources/icon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "Web2MD.app" 175 120 \
        --hide-extension "Web2MD.app" \
        --app-drop-link 425 120 \
        "dist/Web2MD-Installer.dmg" \
        "dist/Web2MD.app"
fi

echo "🎉 Build process completed!"
