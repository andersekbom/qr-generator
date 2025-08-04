# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with specific versions
pip install -r requirements.txt

# Verify installation
python -c "import qr_generator; print('✅ Setup complete!')"
```

### Running Applications
- **Main QR code generator**: `python qr_generator.py`

## Architecture Overview

This is a Python-based QR code generation toolkit with multiple specialized generators:

### Core Components

1. **Main QR Generator** (`qr_generator.py`)
   - Unified application with multiple operation modes
   - CSV import with auto-delimiter detection
   - Manual parameter input for sequential generation
   - Supports both PNG and SVG output formats
   - Advanced configuration options (QR parameters, format-specific settings)
   - Preset system for parameter management
   - Custom filename and directory options

### Key Libraries
- `qrcode`: Core QR code generation (supports PNG, SVG formats)
- `tkinter`: GUI dialogs for user input
- `tqdm`: Progress bars for batch operations
- `Pillow`: Image processing support

### File Structure
- `input/`: Contains CSV files with QR code data
- `output/`: Temporary directory for generated QR codes (auto-cleaned)
- Generated files are automatically zipped and the output directory is cleaned after processing

### Common Patterns
- All generators support both PNG and SVG output formats
- ZIP file creation is standard for batch operations
- Progress tracking with tqdm for long-running operations
- Tkinter-based GUI for user-friendly parameter input
- Automatic output directory management (create/clean)