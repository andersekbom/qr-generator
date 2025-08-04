# QR Generator - Setup and Installation Guide

This guide provides step-by-step instructions for setting up and running the QR Generator application in a Python virtual environment.

## Prerequisites

- Python 3.8 or higher (tested with Python 3.12)
- pip (Python package installer)
- tkinter (usually included with Python installations)

### Checking Prerequisites

```bash
# Check Python version
python --version
# or
python3 --version

# Check if tkinter is available
python -c "import tkinter; print('✅ tkinter is available')"
```

## Installation

### 1. Clone or Download the Project

If using git:
```bash
git clone <repository-url>
cd qr-generator
```

Or download and extract the project files to a directory.

### 2. Create Virtual Environment

Create a new virtual environment in the project directory:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when the virtual environment is active.

### 3. Install Dependencies

Install all required packages using the requirements file:

```bash
pip install -r requirements.txt
```

This will install:
- `qrcode==8.2` - Core QR code generation library
- `tqdm==4.67.1` - Progress bars for batch operations  
- `colorama==0.4.6` - Cross-platform colored console output
- `pillow==11.3.0` - Python Imaging Library for image processing

### 4. Verify Installation

Test that all dependencies are correctly installed:

```bash
python -c "
import qr_generator
print('✅ QR Generator application is ready to use!')

# Test core functionality
result = qr_generator.validate_png_quality('85')
print('✅ Core functions working:', result[0])
"
```

## Running the Application

### Main Application

Run the main QR generator application:

```bash
python qr_generator.py
```

This will open a GUI dialog interface where you can:
- Choose between different generation modes (Single, Batch, CSV)
- Configure QR code parameters
- Set format-specific options (PNG quality, SVG precision)
- Manage parameter presets
- Customize output options

### Test Scripts

Run the test and validation scripts:

```bash
# Test format-specific options
python test_format_options.py

# Test sample data validation
python test_sample_data.py

# Run comprehensive unit tests
python tests/test_core_functions.py
```

## Project Structure

```
qr-generator/
├── qr_generator.py              # Main application
├── requirements.txt             # Python dependencies
├── CLAUDE.md                   # Project documentation
├── SETUP.md                    # This setup guide
├── tasks.md                    # Development roadmap
├── input/                      # Sample CSV files
│   ├── README.md              # Sample data documentation
│   └── *.csv                  # Various sample files
├── tests/                      # Test suite
│   └── test_*.py              # Individual test files
├── test_format_options.py      # Format options testing
├── test_sample_data.py         # Sample data validation
└── venv/                       # Virtual environment (after setup)
```

## Features Overview

### Generation Modes
1. **Single Generation** - Create one or a few QR codes with manual parameters
2. **Batch Sequential** - Generate multiple QR codes with sequential parameters
3. **CSV Batch** - Import data from CSV files for bulk generation

### Supported Formats
- **PNG** - With configurable quality settings (0-100)
- **SVG** - With configurable precision settings (0-10 decimal places)

### CSV Features
- Auto-delimiter detection (comma, semicolon, tab, pipe)
- Column selection
- Header row handling
- Unicode and special character support

### Advanced Options
- QR code version (1-40 or auto)
- Error correction levels (L, M, Q, H)
- Box size and border customization
- Custom filename patterns
- Output directory selection
- Parameter presets for repeated use

## Troubleshooting

### Common Issues

**Import Error for tkinter:**
```bash
# On Ubuntu/Debian:
sudo apt-get install python3-tk

# On CentOS/RHEL:
sudo yum install tkinter
```

**Virtual Environment Not Activating:**
- Ensure you're in the correct directory
- Check that `venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows) exists
- Try recreating the virtual environment

**Missing Dependencies:**
```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

**GUI Not Displaying:**
- Ensure you have a display server running (X11, Wayland)
- For headless servers, QR generation can still work but GUI dialogs will fail
- Consider running tests instead: `python test_format_options.py`

### Verifying Installation

Run this comprehensive test to verify everything is working:

```bash
python -c "
print('🔍 Testing QR Generator Installation...')
print()

# Test imports
try:
    import qr_generator
    import qrcode
    import tqdm
    import PIL
    print('✅ All required modules imported successfully')
except ImportError as e:
    print('❌ Import error:', e)
    exit(1)

# Test core functionality
try:
    result = qr_generator.validate_png_quality('85')
    assert result[0] == True and result[1] == 85
    print('✅ Core validation functions working')
except Exception as e:
    print('❌ Validation error:', e)
    exit(1)

# Test QR code generation
try:
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as temp_dir:
        qr_generator.create_qr_codes(
            valid_uses='1', volume='100', end_date='31.12.25',
            color='#000000', output_folder=temp_dir, format='png',
            count=1
        )
        files = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
        assert len(files) == 1
    print('✅ QR code generation working')
except Exception as e:
    print('❌ QR generation error:', e)
    exit(1)

print()
print('🎉 Installation verified successfully!')
print('Run: python qr_generator.py')
"
```

## Development

### Running Tests

The project includes comprehensive tests:

```bash
# Run all tests
python -m pytest tests/ -v

# Or run individual test files
python tests/test_core_functions.py
python test_format_options.py
python test_sample_data.py
```

### Adding Dependencies

If you add new dependencies:

1. Install the package: `pip install package-name`
2. Update requirements: `pip freeze > requirements.txt`
3. Clean up the requirements file to include only project dependencies

## Support

- Check the `input/README.md` for sample data documentation
- Review `CLAUDE.md` for detailed project architecture
- All tests include comprehensive examples of usage
- See `tasks.md` for the complete development history and features

## System Requirements

- **Minimum**: Python 3.8, 100MB disk space
- **Recommended**: Python 3.10+, 200MB disk space
- **Display**: GUI functionality requires display server (X11/Wayland on Linux)
- **Memory**: ~50MB RAM for normal operation, ~100MB for large CSV files

## License

This project includes comprehensive functionality for QR code generation with advanced features and extensive testing coverage.