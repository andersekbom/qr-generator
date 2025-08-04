# QR Generator

A comprehensive QR code generation toolkit with advanced features, multiple formats, and extensive customization options.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-1.0-brightgreen.svg)

## Features

### 🎯 **Multiple Generation Modes**
- **Single Generation** - Create one or a few QR codes with manual parameters
- **Batch Sequential** - Generate multiple QR codes with sequential parameters  
- **CSV Batch** - Import data from CSV files for bulk generation

### 📱 **Output Formats**
- **PNG** - With configurable quality settings (0-100)
- **SVG** - With configurable precision settings (0-10 decimal places)

### 📊 **CSV Support** 
- Auto-delimiter detection (comma, semicolon, tab, pipe)
- Column selection with GUI dialogs
- Header row handling
- Unicode and special character support

### ⚙️ **Advanced Configuration**
- QR code version (1-40 or auto)
- Error correction levels (L, M, Q, H)
- Box size and border customization
- Custom filename patterns with prefix/suffix
- Output directory selection
- Parameter presets for repeated use

### 🧪 **Testing & Quality**
- 23 comprehensive test files
- Sample data for all delimiter types
- Format-specific option validation
- CSV processing edge case testing
- Complete documentation

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/andersekbom/qr-generator.git
   cd qr-generator
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python qr_generator.py
   ```

## Usage Examples

### GUI Application
The main application provides an intuitive dialog-based interface:

```bash
python qr_generator.py
```

This opens a series of dialogs where you can:
- Choose generation mode (Single/Batch/CSV)
- Configure QR parameters and format options
- Select input files (for CSV mode)
- Customize output settings
- Manage parameter presets

### CSV Mode
Import QR code data from CSV files with various delimiters:

```csv
# sample_websites.csv (comma-separated)
url,name,category
https://www.google.com,Google,Search Engine
https://www.github.com,GitHub,Development

# sample_contacts.csv (pipe-separated)  
name|phone|email
John Doe|555-0123|john@email.com
Jane Smith|555-0124|jane@email.com
```

### Manual Mode
Generate sequential QR codes with customizable payload format:
- Default format: `M-{uses}-{serial}-{volume}-{date}-{security}-{suffix}`
- Example: `M-15-00000001-500-26.12.31-SECD-23FF45EE`

## Testing

Run the comprehensive test suite:

```bash
# Test format-specific options
python tests/test_format_options.py

# Test sample data validation  
python tests/test_sample_data.py

# Test core functions
python tests/test_core_functions.py

# Run all unit tests
python -m pytest tests/ -v
```

## Project Structure

```
qr-generator/
├── qr_generator.py              # Main application
├── requirements.txt             # Dependencies
├── SETUP.md                     # Detailed setup guide
├── CLAUDE.md                    # Development documentation
├── input/                       # Sample CSV files
│   ├── README.md               # Sample data documentation
│   └── sample_*.csv            # Various test files
└── tests/                       # Test suite (23 files)
    ├── test_core_functions.py  # Core functionality tests
    ├── test_format_options.py  # Format-specific tests
    └── test_*.py               # Feature-specific tests
```

## Dependencies

- `qrcode==8.2` - Core QR code generation
- `tqdm==4.67.1` - Progress bars for batch operations
- `colorama==0.4.6` - Cross-platform colored output
- `pillow==11.3.0` - Image processing library

## Requirements

- Python 3.8 or higher
- tkinter (GUI dialogs - usually included with Python)
- Virtual environment recommended

## Sample Data

The project includes comprehensive sample data for testing:

- **Website URLs** (comma delimiter) - Google, GitHub, Stack Overflow, etc.
- **Contact Information** (pipe delimiter) - Names, phones, emails
- **WiFi Networks** (tab delimiter) - SSIDs, passwords, security settings
- **Product Codes** (comma delimiter) - SKUs, barcodes, prices
- **Event Tickets** (semicolon delimiter) - IDs, venues, dates
- **Special Characters** - Unicode, emoji, symbols
- **Large Dataset** - Performance testing with thousands of records

## Development History

This project represents the completion of a comprehensive 20-task enhancement roadmap:

### CSV Import Features ✅
- Auto-delimiter detection
- Column selection dialogs
- Header row handling
- File processing with progress bars

### Advanced Features ✅  
- SVG color handling with XML namespaces
- Configurable payload formats
- Input validation for all parameters
- QR code parameter customization

### User Experience ✅
- Output directory selection
- Filename customization options
- Selective file cleanup
- Parameter preset system
- Batch operation modes

### Quality Assurance ✅
- Format-specific options (PNG quality, SVG precision)
- Comprehensive unit test coverage
- Sample data for all use cases
- Complete documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is released under the MIT License. See the LICENSE file for details.

## Support

- **Setup Issues**: See [SETUP.md](SETUP.md) for detailed installation instructions
- **Sample Data**: Check [input/README.md](input/README.md) for CSV format examples
- **Development**: Review [CLAUDE.md](CLAUDE.md) for project architecture
- **Testing**: All test files include comprehensive usage examples

## Acknowledgments

Built with comprehensive testing and documentation. Generated with assistance from [Claude Code](https://claude.ai/code).

---

**Version 1.0** - Complete QR Generator with all enhancement features implemented