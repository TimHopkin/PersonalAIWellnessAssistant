#!/bin/bash
# Build script for Personal AI Wellness Assistant macOS app
# Creates a standalone .app bundle that can be distributed

set -e  # Exit on any error

echo "🚀 Building Personal AI Wellness Assistant for macOS..."
echo "=================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
else
    print_status "Using existing virtual environment"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing requirements..."
pip install -r requirements.txt

# Install PyInstaller if not already installed
print_status "Installing PyInstaller..."
pip install pyinstaller

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Ensure data directory structure exists
print_status "Setting up data directory structure..."
mkdir -p data/backups

# Create empty files if they don't exist (to prevent runtime errors)
touch data/profile.json
touch data/wellness_plan.json
touch data/progress_data.json
touch data/chat_history.json

# Run PyInstaller with our spec file
print_status "Building application with PyInstaller..."
pyinstaller --clean --noconfirm wellness_assistant.spec

# Check if build was successful
if [ -d "dist/Personal AI Wellness Assistant.app" ]; then
    print_success "Build completed successfully!"
    
    # Get the app size
    APP_SIZE=$(du -sh "dist/Personal AI Wellness Assistant.app" | cut -f1)
    print_status "App bundle size: $APP_SIZE"
    
    # Create a DMG file for distribution (optional)
    print_status "Creating disk image for distribution..."
    if command -v hdiutil &> /dev/null; then
        rm -f "dist/Personal AI Wellness Assistant.dmg"
        hdiutil create -volname "Personal AI Wellness Assistant" \
                      -srcfolder "dist/Personal AI Wellness Assistant.app" \
                      -ov -format UDZO \
                      "dist/Personal AI Wellness Assistant.dmg"
        
        if [ -f "dist/Personal AI Wellness Assistant.dmg" ]; then
            DMG_SIZE=$(du -sh "dist/Personal AI Wellness Assistant.dmg" | cut -f1)
            print_success "DMG created: $DMG_SIZE"
        fi
    else
        print_warning "hdiutil not found, skipping DMG creation"
    fi
    
    echo ""
    print_success "✅ Build Complete!"
    echo "=================================================="
    echo "📦 Your app is ready at:"
    echo "   dist/Personal AI Wellness Assistant.app"
    echo ""
    echo "🚀 To run your app:"
    echo "   Double-click the app in Finder, or run:"
    echo "   open 'dist/Personal AI Wellness Assistant.app'"
    echo ""
    if [ -f "dist/Personal AI Wellness Assistant.dmg" ]; then
        echo "💿 Disk image for distribution:"
        echo "   dist/Personal AI Wellness Assistant.dmg"
        echo ""
    fi
    echo "🔧 To install the app:"
    echo "   Drag the .app file to your Applications folder"
    echo ""
    
else
    print_error "Build failed! Check the output above for errors."
    exit 1
fi

# Deactivate virtual environment
deactivate

echo "🎉 All done!"