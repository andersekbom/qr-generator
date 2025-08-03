#!/usr/bin/env python3
"""Manual test for CSV processing - creates actual QR codes for verification"""

import sys
import os

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csv_generation():
    """
    Test CSV processing by generating actual QR codes from test data
    """
    from generate_qr_codes_gui_loop import create_qr_codes, detect_delimiter
    import csv
    
    # Test file path
    test_csv = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'input', 'test_urls.csv')
    
    print("Testing CSV QR code generation:")
    print("-" * 40)
    print(f"Using test file: {test_csv}")
    
    try:
        # Detect delimiter
        delimiter = detect_delimiter(test_csv)
        print(f"Detected delimiter: '{delimiter}'")
        
        # Read CSV data
        with open(test_csv, "r") as infile:
            reader = csv.reader(infile, delimiter=delimiter)
            next(reader)  # Skip header
            rows = list(reader)
        
        print(f"Found {len(rows)} data rows")
        
        # Create output directory
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate QR codes
        print("Generating QR codes...")
        create_qr_codes(
            valid_uses=None,
            volume=None, 
            end_date=None,
            color="#0066CC",
            output_folder=output_dir,
            format="png",
            count=None,
            csv_data=rows,
            input_column=0  # URL column
        )
        
        # Check generated files
        generated_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
        print(f"Generated {len(generated_files)} QR code files:")
        for file in generated_files:
            print(f"  - {file}")
        
        print(f"\n✅ Test completed successfully!")
        print(f"📁 QR codes saved in: {output_dir}/")
        print("🔍 You can verify the QR codes by scanning them with a QR reader")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_csv_generation()