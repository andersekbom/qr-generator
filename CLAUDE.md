# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running Applications
- **GUI-based QR code generator (from CSV)**: `python generate_qr_codes_gui.py`
- **GUI-based QR code generator (with color support)**: `python generate_qr_codes_gui_loop.py` 
- **Batch QR code generator (predefined format)**: `python generate_qr_codes_bw.py`
- **Colored QR code generator (single file)**: `python colored_qr_works.py`

## Architecture Overview

This is a Python-based QR code generation toolkit with multiple specialized generators:

### Core Components

1. **CSV-based Generator** (`generate_qr_codes.py`, `generate_qr_codes_gui.py`)
   - Reads data from CSV files in `input/` directory
   - Auto-detects CSV delimiters
   - Supports configurable column selection
   - Outputs to `output/` directory with automatic cleanup

2. **Batch Generator** (`generate_qr_codes_bw.py`)
   - Generates QR codes with predefined payload format: `M-{usage_limit}-{volume}-{sequence}-{expiry_date}`
   - Designed for serialized code generation (e.g., product codes, vouchers)

3. **Colored QR Generator** (`colored_qr_works.py`)
   - Generates single SVG QR codes with custom colors
   - Uses XML manipulation to ensure proper color application
   - Supports both foreground and background color customization

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