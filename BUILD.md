# 📦 Building QR Generator for Distribution

This guide explains how to package the QR Generator as standalone applications for Linux, macOS, and Windows.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Git** (for cloning the repository)  
3. **Virtual environment** (recommended)

### Platform-Specific Requirements

#### Linux (Ubuntu/Debian/CentOS/RHEL)
```bash
# Install system dependencies
sudo apt update && sudo apt install python3-dev python3-venv python3-tk upx-ucl
# OR for RHEL/CentOS: sudo yum install python3-devel python3-tkinter upx
```

#### macOS (10.13+)
```bash
# Install Xcode command line tools
xcode-select --install

# Install Homebrew (optional, for upx)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install upx  # Optional: for smaller executables
```

#### Windows (10/11)
```cmd
# Install Python from https://python.org (include pip and tkinter)
# Install Visual Studio Build Tools (if needed for some packages)
# Optional: Install NSIS from https://nsis.sourceforge.io/ for installers
```

## 🔧 Build Process

### 1. Prepare Environment

```bash
# Clone the repository
git clone https://github.com/andersekbom/qr-generator.git
cd qr-generator

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR: venv\Scripts\activate.bat  # Windows

# Install runtime and build dependencies
pip install -r requirements.txt
pip install -r build_requirements.txt
```

### 2. Platform-Specific Builds

#### 🐧 Linux Build
```bash
./build_linux.sh
```
**Outputs:**
- `dist/QRGenerator/` - PyInstaller executable bundle
- `dist/QRGenerator-Linux-v2.0.tar.gz` - Distribution archive
- `dist/QRGenerator.AppDir/` - AppImage source (run appimagetool to create .AppImage)

#### 🍎 macOS Build  
```bash
./build_macos.sh
```
**Outputs:**
- `dist/QRGenerator.app` - Native macOS app bundle
- `dist/QRGenerator-macOS-v2.0.dmg` - DMG installer
- `dist/QRGenerator-macOS-v2.0.zip` - ZIP archive

#### 🪟 Windows Build
```cmd
build_windows.bat
```
**Outputs:**
- `dist/QRGenerator/` - PyInstaller executable bundle
- `dist/QRGenerator-Windows-v2.0.zip` - Distribution archive
- `dist/installer.nsi` - NSIS installer script

## 🛠️ Build Tools Used

### Primary: PyInstaller
- **Best for:** Most reliable, good platform support
- **Configuration:** `qr_generator.spec`
- **Features:** Single-file or directory bundles, auto-dependency detection

### Alternative: cx_Freeze
- **Best for:** When PyInstaller has issues
- **Configuration:** `setup.py`
- **Features:** Cross-platform, good for debugging

## 📋 Build Outputs Explained

### Linux Distributions
1. **Standalone Directory** (`dist/QRGenerator/`)
   - Run directly: `./QRGenerator`
   - Contains all dependencies
   - ~50-100MB

2. **Tar.gz Archive** (`QRGenerator-Linux-v2.0.tar.gz`)
   - Extract and run
   - Easy distribution

3. **AppImage** (`QRGenerator.AppDir/`)
   - Single-file executable  
   - Run: `./QRGenerator-v2.0.AppImage`
   - Requires appimagetool to build

### macOS Distributions  
1. **App Bundle** (`QRGenerator.app`)
   - Native macOS application
   - Double-click to run
   - Integrates with macOS

2. **DMG Installer** (`QRGenerator-macOS-v2.0.dmg`)
   - Standard macOS installer
   - Drag-and-drop installation
   - Professional distribution method

### Windows Distributions
1. **Standalone Directory** (`dist/QRGenerator/`)
   - Run: `QRGenerator.exe`
   - Portable application
   - No installation required

2. **ZIP Archive** (`QRGenerator-Windows-v2.0.zip`)
   - Extract and run
   - Easy distribution

3. **NSIS Installer** (requires NSIS)
   - Professional installer
   - Start menu integration
   - Uninstaller included

## 🔍 Testing Your Build

### Before Distribution
1. **Test on clean system** (VM recommended)
2. **Verify all features work:**
   - GUI loads properly
   - File dialogs work
   - QR generation functions
   - CSV import works
   - Presets save/load
   - Theme switching works

3. **Check file associations:**
   - CSV files (if configured)
   - Icon display

### Common Issues & Solutions

#### Import Errors
- **Problem:** Missing modules in frozen app
- **Solution:** Add to `hiddenimports` in `qr_generator.spec`

#### GUI Scaling Issues
- **Problem:** Blurry interface on high-DPI displays
- **Solution:** Already configured in spec files

#### File Path Issues
- **Problem:** Can't find data files (icons, presets)
- **Solution:** Verify `datas` section in spec files

#### Large File Size
- **Problem:** Executable is too large (>200MB)
- **Solution:** Add more modules to `excludes` in spec files

## 🎯 Distribution Best Practices

### Code Signing & Notarization

#### macOS
```bash
# Sign the app (requires Developer ID)
codesign --force --sign "Developer ID Application: Your Name" dist/QRGenerator.app

# Notarize for Gatekeeper (requires Apple Developer account)
./dist/notarize.sh your-apple-id@email.com your-app-password
```

#### Windows
```cmd
# Sign with certificate (requires code signing certificate)
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com dist/QRGenerator/QRGenerator.exe
```

### File Compression
- **UPX**: Reduces executable size by 50-70%
- **Already enabled** in build scripts
- **Install:** `apt install upx-ucl` (Linux) or `brew install upx` (macOS)

### Virus Scanner False Positives
- **Common with PyInstaller executables**
- **Solutions:**
  1. Submit to virus scanner vendors
  2. Use code signing certificates
  3. Build from clean environment

## 📁 File Structure After Build

```
dist/
├── QRGenerator/                    # PyInstaller output
│   ├── QRGenerator(.exe)          # Main executable  
│   ├── _internal/                 # Dependencies
│   ├── src/                       # Your modules
│   ├── input/                     # Sample data
│   ├── presets/                   # Preset files
│   └── icons...                   # Application icons
├── QRGenerator-Platform-v2.0.*    # Distribution packages
└── build-specific files           # Platform installers
```

## 🚀 Advanced Build Options

### Custom PyInstaller Options

```bash
# Single-file executable (slower startup)
pyinstaller --onefile qr_generator.py

# Debug mode (shows console)
pyinstaller --debug=all qr_generator.spec

# Custom icon
pyinstaller --icon=custom_icon.ico qr_generator.py

# Exclude unnecessary modules
pyinstaller --exclude-module=matplotlib qr_generator.py
```

### Environment Variables

```bash
# PyInstaller cache location
export PYINSTALLER_CACHE_DIR=/tmp/pyinstaller_cache

# UPX compression level (0-9)  
export UPX_LEVEL=9
```

## 🔗 Useful Links

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [cx_Freeze Documentation](https://cx-freeze.readthedocs.io/)
- [NSIS Installer](https://nsis.sourceforge.io/)
- [AppImage Documentation](https://appimage.org/)
- [macOS Code Signing](https://developer.apple.com/documentation/xcode/notarizing_macos_software_before_distribution)

---

## 📞 Support

If you encounter issues during the build process:

1. Check the build logs for specific error messages
2. Ensure all dependencies are installed
3. Try the alternative build method (cx_Freeze vs PyInstaller)
4. Test on a clean virtual machine
5. Check the GitHub Issues page for known problems

**Happy building! 🎉**