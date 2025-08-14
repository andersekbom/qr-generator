#!/bin/bash
# Build script for Linux (Ubuntu/Debian/CentOS/RHEL)

set -e  # Exit on any error

echo "🐧 Building QR Generator for Linux..."

# Check if we're in the right directory
if [ ! -f "qr_generator.py" ]; then
    echo "❌ Error: qr_generator.py not found. Run this script from the project root directory."
    exit 1
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
mkdir -p dist/QRGenerator-Linux
cp -r dist/QRGenerator/* dist/QRGenerator-Linux/

# Create AppImage directory structure (for Linux AppImage packaging)
mkdir -p dist/QRGenerator.AppDir/usr/bin
mkdir -p dist/QRGenerator.AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p dist/QRGenerator.AppDir/usr/share/applications

# Copy files for AppImage
cp -r dist/QRGenerator/* dist/QRGenerator.AppDir/usr/bin/
cp icon_256.png dist/QRGenerator.AppDir/usr/share/icons/hicolor/256x256/apps/qrgenerator.png
cp icon_256.png dist/QRGenerator.AppDir/qrgenerator.png

# Create .desktop file for AppImage
cat > dist/QRGenerator.AppDir/qrgenerator.desktop << 'EOF'
[Desktop Entry]
Name=QR Generator Pro
Comment=Professional QR Code Generation Tool
Exec=QRGenerator
Icon=qrgenerator
Type=Application
Categories=Graphics;Photography;
Keywords=qr;code;generator;barcode;
StartupNotify=true
MimeType=text/csv;
EOF

# Copy desktop file to applications directory
cp dist/QRGenerator.AppDir/qrgenerator.desktop dist/QRGenerator.AppDir/usr/share/applications/

# Create AppRun script
cat > dist/QRGenerator.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin/:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib/:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${HERE}/usr/share/:${XDG_DATA_DIRS}"
cd "${HERE}/usr/bin"
exec "${HERE}/usr/bin/QRGenerator" "$@"
EOF

chmod +x dist/QRGenerator.AppDir/AppRun

# Create tarball for distribution
echo "📦 Creating distribution archive..."
cd dist
tar -czf QRGenerator-Linux-v2.0.tar.gz QRGenerator-Linux/
cd ..

# Show build results
echo ""
echo "✅ Build completed successfully!"
echo ""
echo "📁 Build outputs:"
echo "   • PyInstaller build: dist/QRGenerator/"
echo "   • cx_Freeze build: build/exe.linux-*/"
echo "   • Linux package: dist/QRGenerator-Linux-v2.0.tar.gz"
echo "   • AppImage ready: dist/QRGenerator.AppDir/ (use appimagetool to create .AppImage)"
echo ""
echo "🚀 To create AppImage:"
echo "   1. Download appimagetool: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
echo "   2. Make it executable: chmod +x appimagetool-x86_64.AppImage"
echo "   3. Create AppImage: ./appimagetool-x86_64.AppImage dist/QRGenerator.AppDir/"
echo ""
echo "📋 To test the build:"
echo "   ./dist/QRGenerator/QRGenerator"