#!/bin/bash
# Build script for macOS (macOS 10.13+)

set -e  # Exit on any error

echo "🍎 Building QR Generator for macOS..."

# Check if we're in the right directory
if [ ! -f "qr_generator.py" ]; then
    echo "❌ Error: qr_generator.py not found. Run this script from the project root directory."
    exit 1
fi

# Check for macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: This script is designed for macOS. You may encounter issues on other platforms."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install build requirements
echo "📥 Installing build dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r build_requirements.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/ *.egg-info/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Build with PyInstaller (primary method) 
echo "🔨 Building with PyInstaller..."
pyinstaller qr_generator.spec --clean --noconfirm

# Build with cx_Freeze (alternative method)
echo "🔨 Building with cx_Freeze (alternative)..."
python setup.py build

# Create distribution directory structure
echo "📦 Creating distribution package..."
mkdir -p "dist/QRGenerator-macOS"

# Copy the .app bundle
if [ -d "dist/QRGenerator.app" ]; then
    cp -r "dist/QRGenerator.app" "dist/QRGenerator-macOS/"
else
    echo "⚠️  .app bundle not found, copying executable instead"
    cp -r dist/QRGenerator/* "dist/QRGenerator-macOS/"
fi

# Create DMG installer structure
echo "📦 Creating DMG installer structure..."
mkdir -p "dist/dmg-staging"
if [ -d "dist/QRGenerator.app" ]; then
    cp -r "dist/QRGenerator.app" "dist/dmg-staging/"
else
    mkdir -p "dist/dmg-staging/QRGenerator"
    cp -r dist/QRGenerator/* "dist/dmg-staging/QRGenerator/"
fi

# Create Applications symlink for DMG
ln -sf /Applications "dist/dmg-staging/Applications"

# Create background image for DMG (optional)
if [ -f "icon_256.png" ]; then
    cp icon_256.png "dist/dmg-staging/.background.png"
fi

# Create DMG using hdiutil (macOS built-in tool)
echo "📦 Creating DMG installer..."
hdiutil create -srcfolder "dist/dmg-staging" \
    -volname "QR Generator Pro" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDZO \
    -imagekey zlib-level=9 \
    "dist/QRGenerator-macOS-v2.0.dmg"

# Code signing (if developer certificate is available)
if command -v codesign >/dev/null 2>&1; then
    echo "🔐 Checking for code signing certificate..."
    CERT_NAME=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | sed 's/.*"\(.*\)".*/\1/' || echo "")
    
    if [ ! -z "$CERT_NAME" ]; then
        echo "🔐 Code signing with certificate: $CERT_NAME"
        if [ -d "dist/QRGenerator.app" ]; then
            codesign --force --verify --verbose --sign "$CERT_NAME" "dist/QRGenerator.app"
            codesign --force --verify --verbose --sign "$CERT_NAME" "dist/QRGenerator-macOS/QRGenerator.app"
        else
            echo "⚠️  Skipping code signing (no .app bundle found)"
        fi
        
        # Sign the DMG
        codesign --force --verify --verbose --sign "$CERT_NAME" "dist/QRGenerator-macOS-v2.0.dmg"
    else
        echo "⚠️  No code signing certificate found. App will show as 'unidentified developer'"
        echo "   To fix this, get a Developer ID certificate from Apple Developer Program"
    fi
else
    echo "⚠️  codesign not available"
fi

# Create ZIP for distribution (alternative to DMG)
echo "📦 Creating ZIP archive..."
cd dist
zip -r "QRGenerator-macOS-v2.0.zip" "QRGenerator-macOS/"
cd ..

# Create app notarization script (for distribution outside Mac App Store)
cat > dist/notarize.sh << 'EOF'
#!/bin/bash
# Apple notarization script (requires Apple Developer account)
# Usage: ./notarize.sh <apple-id> <app-specific-password>

if [ $# -ne 2 ]; then
    echo "Usage: $0 <apple-id> <app-specific-password>"
    echo "Get app-specific password from: https://appleid.apple.com/account/manage"
    exit 1
fi

APPLE_ID="$1"
APP_PASSWORD="$2"
DMG_FILE="QRGenerator-macOS-v2.0.dmg"

echo "🔐 Uploading for notarization..."
xcrun notarytool submit "$DMG_FILE" --apple-id "$APPLE_ID" --password "$APP_PASSWORD" --team-id <YOUR_TEAM_ID> --wait

echo "🔐 Stapling notarization ticket..."
xcrun stapler staple "$DMG_FILE"

echo "✅ Notarization complete!"
EOF

chmod +x dist/notarize.sh

# Show build results
echo ""
echo "✅ Build completed successfully!"
echo ""
echo "📁 Build outputs:"
echo "   • PyInstaller build: dist/QRGenerator.app (if successful)"
echo "   • cx_Freeze build: build/exe.macosx-*/"
echo "   • macOS package: dist/QRGenerator-macOS-v2.0.zip"
echo "   • DMG installer: dist/QRGenerator-macOS-v2.0.dmg"
echo "   • Notarization script: dist/notarize.sh"
echo ""
echo "🚀 For distribution:"
echo "   1. Test: open dist/QRGenerator.app"
echo "   2. For Mac App Store: Use Xcode to upload"
echo "   3. For direct distribution: Use the DMG file"
echo "   4. For notarization: ./dist/notarize.sh <apple-id> <app-password>"
echo ""
echo "📋 To test the build:"
if [ -d "dist/QRGenerator.app" ]; then
    echo "   open dist/QRGenerator.app"
else
    echo "   ./dist/QRGenerator/QRGenerator"
fi