# Sample Data for QR Code Generator Testing

This directory contains various sample CSV files designed to test different aspects of the QR code generator application. Each file demonstrates different CSV formats, delimiters, and data types.

## Sample Files Overview

### 1. Basic Website URLs
- **File**: `sample_websites.csv`
- **Delimiter**: Comma (`,`)
- **Columns**: url, name, category, description
- **Use Case**: Testing URL QR code generation with multiple columns
- **Test Scenarios**: Column selection, header row handling, URL validation

### 2. Contact Information
- **File**: `sample_contact_info.csv`
- **Delimiter**: Pipe (`|`)
- **Columns**: name, phone, email, company
- **Use Case**: Testing pipe delimiter detection and contact QR codes
- **Test Scenarios**: Different delimiter handling, contact card generation

### 3. WiFi Network Information
- **File**: `sample_wifi_networks.csv`
- **Delimiter**: Tab (`\t`)
- **Columns**: ssid, password, security, hidden
- **Use Case**: Testing tab delimiter and WiFi QR code generation
- **Test Scenarios**: Tab delimiter detection, WiFi credential QR codes

### 4. Product Information
- **File**: `sample_product_codes.csv`
- **Delimiter**: Comma (`,`)
- **Columns**: product_id, product_name, sku, barcode, price
- **Use Case**: Testing product/inventory QR codes
- **Test Scenarios**: Numeric data handling, SKU/barcode QR generation

### 5. Special Characters and Unicode
- **File**: `sample_special_characters.csv`
- **Delimiter**: Comma (`,`)
- **Columns**: text, description
- **Use Case**: Testing special character handling and filename safety
- **Test Scenarios**: Unicode support, special character encoding, safe filename generation

### 6. Minimal Dataset
- **File**: `sample_minimal.csv`
- **Delimiter**: Comma (`,`)
- **Columns**: data
- **Use Case**: Testing single-column CSV processing
- **Test Scenarios**: Minimal CSV structure, single column selection

### 7. Event Tickets
- **File**: `sample_event_tickets.csv`
- **Delimiter**: Semicolon (`;`)
- **Columns**: ticket_id, event_name, date, venue, seat, price
- **Use Case**: Testing semicolon delimiter and event ticket QR codes
- **Test Scenarios**: Semicolon delimiter detection, ticket information encoding

## Existing Production Data

### 8. Legacy QR Codes
- **File**: `qr-codes.csv`
- **Delimiter**: Comma (`,`)
- **Columns**: serial, col1, col2
- **Use Case**: Legacy data compatibility testing

### 9. URL Collection
- **File**: `test_urls.csv`
- **Delimiter**: Comma (`,`)
- **Columns**: url, description
- **Use Case**: Simple URL QR code generation

### 10. Serial Numbers (Large Dataset)
- **Files**: `bw_serials.csv`, `bw_serials_15use.csv`, `bw_serials_single_use.csv`
- **Delimiter**: Semicolon (`;`)
- **Columns**: Serial, Counter, Valid uses, Volume (ml), Uses Left, Last Used, Status, Beverage Used
- **Use Case**: Large dataset processing, batch QR code generation
- **Test Scenarios**: Performance testing, large file handling, progress bar functionality

## Testing Scenarios

### Delimiter Detection Testing
Use these files to test the `detect_delimiter()` function:
- Comma: `sample_websites.csv`, `sample_product_codes.csv`, `sample_minimal.csv`
- Semicolon: `sample_event_tickets.csv`, `bw_serials.csv`
- Tab: `sample_wifi_networks.csv`
- Pipe: `sample_contact_info.csv`

### Column Selection Testing
Files with multiple columns for testing column selection dialogs:
- `sample_websites.csv` (4 columns)
- `sample_contact_info.csv` (4 columns)
- `sample_wifi_networks.csv` (4 columns)
- `sample_product_codes.csv` (5 columns)
- `sample_event_tickets.csv` (6 columns)
- `bw_serials.csv` (8 columns)

### Header Row Testing
All sample files include header rows to test the "skip first row" functionality.

### Special Character Testing
- `sample_special_characters.csv` contains various Unicode characters, symbols, and formatting
- Tests filename safety and QR code encoding capabilities

### Performance Testing
- `bw_serials.csv` contains thousands of records for testing:
  - Large file processing
  - Progress bar functionality
  - Memory usage optimization
  - Batch processing performance

## Usage Examples

### CSV Mode Testing
1. **Basic URL QR Codes**: Use `sample_websites.csv`, select column 0 (url)
2. **Contact Information**: Use `sample_contact_info.csv`, select column 2 (email)
3. **WiFi Networks**: Use `sample_wifi_networks.csv`, select column 0 (ssid)
4. **Product Codes**: Use `sample_product_codes.csv`, select column 2 (sku)
5. **Event Tickets**: Use `sample_event_tickets.csv`, select column 0 (ticket_id)

### Delimiter Testing
1. Load each file and verify the correct delimiter is detected
2. Test manual delimiter override functionality
3. Verify CSV parsing works correctly with different delimiters

### Error Handling Testing
1. Try loading non-existent files
2. Test with empty CSV files
3. Test with malformed CSV structure
4. Test column selection beyond available columns

## File Formats and Standards

All sample files follow these standards:
- UTF-8 encoding for Unicode compatibility
- Consistent column naming (lowercase with underscores)
- Realistic data that represents actual use cases
- Various data types (URLs, text, numbers, dates, special characters)
- Different row counts for scalability testing

## Adding New Sample Data

When adding new sample files:
1. Use descriptive filenames with `sample_` prefix
2. Include different delimiter types for comprehensive testing
3. Add realistic data that represents actual use cases
4. Include a variety of data types and special cases
5. Update this README with file description and use cases
6. Test with the application to ensure compatibility

## Test Data Maintenance

- Keep sample files small enough for quick testing (< 100 rows)
- Use `bw_serials.csv` for large dataset testing
- Regularly verify files are valid CSV format
- Ensure UTF-8 encoding is maintained
- Test files with different operating systems and CSV readers