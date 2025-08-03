# QR Generator Enhancement Tasks

Base file: `generate_qr_codes_gui_loop.py`

## CSV Import Features (from generate_qr_codes_gui.py)

### Task 1: Add CSV delimiter detection function ✅ COMPLETED
**Start**: Add `detect_delimiter()` function to the base file  
**End**: Function exists and can detect CSV delimiters from file samples  
**Test**: Create test CSV with different delimiters, verify correct detection  
**Source**: `generate_qr_codes_gui.py:12-15`  
**Status**: ✅ Function added, csv import added, test created in `tests/test_delimiter.py`, all delimiters (comma, semicolon, tab, pipe) tested successfully

### Task 2: Add CSV file selection dialog ✅ COMPLETED
**Start**: Add file dialog option to main() function  
**End**: User can choose between CSV input mode or manual parameter mode  
**Test**: Run program, verify file dialog appears when CSV mode selected  
**Source**: `generate_qr_codes_gui.py:53`  
**Status**: ✅ Added input mode selection dialog, CSV file dialog implemented, test created in `tests/test_csv_dialog.py`, fallback to manual mode when CSV not implemented

### Task 3: Add CSV processing logic ✅ COMPLETED
**Start**: Add CSV reading and row processing to create_qr_codes function  
**End**: Function can process CSV files with configurable column selection  
**Test**: Process sample CSV file, verify QR codes generated from CSV data  
**Source**: `generate_qr_codes_gui.py:70-77`  
**Status**: ✅ Enhanced create_qr_codes() with CSV mode, added full CSV workflow to main(), safe filename generation, comprehensive tests in `tests/test_csv_processing.py` and `tests/test_csv_manual.py`, sample CSV created in `input/test_urls.csv`

### Task 4: Add column selection dialog ✅ COMPLETED
**Start**: Add input dialog for column selection when CSV mode chosen  
**End**: User can specify which CSV column contains QR code data  
**Test**: Test with multi-column CSV, verify correct column data used  
**Source**: `generate_qr_codes_gui.py:60`  
**Status**: ✅ Already implemented via simpledialog.askinteger() on line 118, comprehensive tests created in `tests/test_column_selection.py`, supports multi-column CSV processing with invalid column handling

### Task 5: Add skip header row option ✅ COMPLETED
**Start**: Add checkbox/dialog for skipping first CSV row  
**End**: User can choose to skip header row in CSV processing  
**Test**: Test with CSV having headers, verify first row skipped when selected  
**Source**: `generate_qr_codes_gui.py:61,72`  
**Status**: ✅ Already implemented via messagebox.askyesno() on line 119, tests created in `tests/test_header_skip.py`, properly skips header row when selected

## Advanced SVG Color Handling (from colored_qr_works.py)

### Task 6: Add XML namespace handling for SVG ✅ COMPLETED
**Start**: Replace regex-based SVG coloring with XML manipulation  
**End**: `colorize_svg()` function uses proper XML parsing with namespaces  
**Test**: Generate colored SVG, verify XML structure and color attributes correct  
**Source**: `colored_qr_works.py:43-61`  
**Status**: ✅ Replaced regex-based SVG coloring with proper XML manipulation, added namespace handling with fallback support, handles both path and rect-based SVG elements, comprehensive tests in `tests/test_svg_colorization.py`

### Task 7: Add background color support for SVG ✅ COMPLETED
**Start**: Extend SVG colorization to handle background colors  
**End**: Both foreground and background colors properly set in SVG files  
**Test**: Generate SVG with custom background color, verify both colors applied  
**Source**: `colored_qr_works.py:58-61`  
**Status**: ✅ Added background_color parameter to colorize_svg(), properly handles background rect elements, supports both foreground and background color customization, tests created in `tests/test_svg_background_color.py`

### Task 8: Add SVG generation error handling ✅ COMPLETED
**Start**: Add proper error handling to SVG color manipulation  
**End**: Graceful handling when SVG elements not found, with warning messages  
**Test**: Generate malformed SVG, verify error handling works without crashes  
**Source**: `colored_qr_works.py:55-56`  
**Status**: ✅ Added comprehensive error handling with fallback to regex method, graceful handling of XML parsing errors, warning messages for missing elements, fallback chain: XML → regex → error reporting

## Code Quality Improvements

### Task 9: Fix hardcoded payload format
**Start**: Make payload components (SECD, 23FF45EE) configurable parameters  
**End**: User can customize security code and suffix in payload  
**Test**: Generate QR codes with different security codes, verify payload format  
**Current**: Hardcoded in `generate_qr_codes_gui_loop.py:20`

### Task 10: Add input validation for all parameters
**Start**: Add validation for valid_uses, volume, end_date, color format  
**End**: All user inputs validated with appropriate error messages  
**Test**: Enter invalid inputs (negative numbers, bad dates, invalid colors), verify errors  
**Current**: Basic validation exists but incomplete

### Task 11: Add progress bar for CSV processing
**Start**: Extend tqdm progress bar to work with CSV mode  
**End**: Progress bar shows during both CSV and manual generation modes  
**Test**: Process large CSV file, verify progress bar displays correctly  
**Source**: Uses existing tqdm implementation

### Task 12: Add configurable QR code parameters
**Start**: Add dialogs for version, error correction, box_size, border settings  
**End**: User can customize QR code generation parameters via GUI  
**Test**: Generate QR codes with different parameters, verify settings applied  
**Current**: Hardcoded in qrcode.QRCode() calls

## File Management Enhancements

### Task 13: Add output directory selection
**Start**: Add dialog to choose output directory instead of hardcoded "output"  
**End**: User can specify where generated files are saved  
**Test**: Select different output directories, verify files saved correctly  
**Current**: Hardcoded "output" directory

### Task 14: Add filename customization options
**Start**: Add options for custom filename patterns/prefixes  
**End**: User can customize how generated files are named  
**Test**: Generate files with different naming patterns, verify names correct  
**Current**: Uses payload as filename

### Task 15: Add selective file cleanup option
**Start**: Make output folder cleanup optional via user choice  
**End**: User can choose to keep generated files after zipping  
**Test**: Generate and zip files, verify cleanup option works as selected  
**Current**: Always cleans up files

## User Experience Improvements

### Task 16: Add parameter preset saving/loading
**Start**: Add functionality to save common parameter combinations  
**End**: User can save and load parameter presets for repeated use  
**Test**: Save preset, load it later, verify all parameters restored correctly  
**New feature**

### Task 17: Add batch operation mode selection
**Start**: Add GUI option to choose between single/batch generation modes  
**End**: Cleaner interface separating different generation workflows  
**Test**: Switch between modes, verify appropriate dialogs appear  
**Current**: Mixed interface

### Task 18: Add format-specific options
**Start**: Show format-specific options (PNG quality, SVG precision) based on selection  
**End**: Advanced options available per format type  
**Test**: Select different formats, verify appropriate options shown  
**New feature**

## Testing Infrastructure

### Task 19: Add unit tests for core functions
**Start**: Create test file with tests for detect_delimiter, create_qr_codes, colorize_svg  
**End**: Comprehensive test coverage for all utility functions  
**Test**: Run test suite, verify all functions work correctly  
**New requirement**

### Task 20: Add sample data for testing
**Start**: Create sample CSV files and test data in input/ directory  
**End**: Standardized test data available for development and testing  
**Test**: Use sample data with application, verify correct processing  
**New requirement**