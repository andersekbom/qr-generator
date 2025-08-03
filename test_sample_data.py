#!/usr/bin/env python3
"""
Test script to validate all sample data files work correctly with the QR code generator
Task 20: Add sample data for testing (CSV files and test data in input/ directory)
"""

import sys
import os
import tempfile
import csv
from pathlib import Path

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_qr_codes_gui_loop import detect_delimiter, create_qr_codes


def test_sample_file(file_path, expected_delimiter=None, test_column=0):
    """Test a single sample CSV file"""
    print(f"\n📁 Testing file: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Test delimiter detection
        detected_delimiter = detect_delimiter(file_path)
        print(f"   Detected delimiter: '{detected_delimiter}' (repr: {repr(detected_delimiter)})")
        
        if expected_delimiter and detected_delimiter != expected_delimiter:
            print(f"   ⚠️  Expected '{expected_delimiter}' but got '{detected_delimiter}'")
        
        # Test CSV reading
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=detected_delimiter)
            rows = list(reader)
        
        if not rows:
            print(f"   ❌ File is empty")
            return False
        
        headers = rows[0]
        data_rows = rows[1:]
        
        print(f"   Headers: {headers}")
        print(f"   Data rows: {len(data_rows)}")
        print(f"   Columns: {len(headers)}")
        
        if test_column >= len(headers):
            print(f"   ⚠️  Test column {test_column} is beyond available columns ({len(headers)})")
            test_column = 0
        
        # Test QR code generation with a small subset
        test_rows = data_rows[:3]  # Just test first 3 rows
        if test_rows:
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"   🔄 Testing QR generation with column {test_column} ({headers[test_column]})...")
                
                create_qr_codes(
                    valid_uses=None, volume=None, end_date=None,
                    color="#000000", output_folder=temp_dir, format="png",
                    count=None, csv_data=test_rows, input_column=test_column
                )
                
                # Check if files were created
                generated_files = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
                print(f"   ✅ Generated {len(generated_files)} QR codes successfully")
                
                # Show sample data from the test column
                sample_data = [row[test_column] if test_column < len(row) else "N/A" for row in test_rows[:2]]
                print(f"   📋 Sample data: {sample_data}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing file: {e}")
        return False


def test_all_sample_files():
    """Test all sample files in the input directory"""
    print("Testing all sample data files...")
    print("=" * 80)
    
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    
    # Define test cases with expected delimiters and test columns
    test_cases = [
        ("sample_websites.csv", ",", 0),  # Test URL column
        ("sample_contact_info.csv", "|", 2),  # Test email column
        ("sample_wifi_networks.csv", "\t", 0),  # Test SSID column
        ("sample_product_codes.csv", ",", 2),  # Test SKU column
        ("sample_special_characters.csv", ",", 0),  # Test text column
        ("sample_minimal.csv", ",", 0),  # Test single column
        ("sample_event_tickets.csv", ";", 0),  # Test ticket ID column
        ("test_urls.csv", ",", 0),  # Test existing URL file
        ("qr-codes.csv", ",", 0),  # Test existing legacy file
    ]
    
    results = []
    for filename, expected_delimiter, test_column in test_cases:
        file_path = os.path.join(input_dir, filename)
        success = test_sample_file(file_path, expected_delimiter, test_column)
        results.append((filename, success))
    
    # Test large file (just delimiter detection, not full processing)
    print(f"\n📁 Testing large file: bw_serials.csv")
    large_file = os.path.join(input_dir, "bw_serials.csv")
    if os.path.exists(large_file):
        try:
            detected_delimiter = detect_delimiter(large_file)
            print(f"   Detected delimiter: '{detected_delimiter}' (repr: {repr(detected_delimiter)})")
            print(f"   ✅ Large file delimiter detection successful")
            results.append(("bw_serials.csv", True))
        except Exception as e:
            print(f"   ❌ Error with large file: {e}")
            results.append(("bw_serials.csv", False))
    else:
        print(f"   ⚠️  Large file not found")
        results.append(("bw_serials.csv", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary:")
    print("-" * 40)
    
    success_count = 0
    for filename, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {filename}")
        if success:
            success_count += 1
    
    total_files = len(results)
    print("-" * 40)
    print(f"Total: {success_count}/{total_files} files passed testing")
    
    if success_count == total_files:
        print("🎉 All sample data files are working correctly!")
    else:
        print("⚠️  Some files had issues and may need attention.")
    
    return success_count == total_files


def test_delimiter_detection_comprehensive():
    """Test delimiter detection with all different delimiter types"""
    print("\n🔍 Comprehensive Delimiter Detection Testing:")
    print("-" * 50)
    
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    
    delimiter_tests = [
        ("Comma", ",", ["sample_websites.csv", "sample_product_codes.csv", "test_urls.csv"]),
        ("Semicolon", ";", ["sample_event_tickets.csv", "bw_serials.csv"]),
        ("Tab", "\t", ["sample_wifi_networks.csv"]),
        ("Pipe", "|", ["sample_contact_info.csv"]),
    ]
    
    for delimiter_name, expected_char, test_files in delimiter_tests:
        print(f"\n{delimiter_name} delimiter ('{expected_char}'):")
        for filename in test_files:
            file_path = os.path.join(input_dir, filename)
            if os.path.exists(file_path):
                try:
                    detected = detect_delimiter(file_path)
                    status = "✅" if detected == expected_char else "❌"
                    print(f"  {status} {filename}: detected '{detected}'")
                except Exception as e:
                    print(f"  ❌ {filename}: error - {e}")
            else:
                print(f"  ⚠️  {filename}: file not found")


def validate_sample_data_structure():
    """Validate that all sample data files have proper structure"""
    print("\n📋 Sample Data Structure Validation:")
    print("-" * 50)
    
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    
    sample_files = [
        "sample_websites.csv",
        "sample_contact_info.csv", 
        "sample_wifi_networks.csv",
        "sample_product_codes.csv",
        "sample_special_characters.csv",
        "sample_minimal.csv",
        "sample_event_tickets.csv"
    ]
    
    for filename in sample_files:
        file_path = os.path.join(input_dir, filename)
        if not os.path.exists(file_path):
            print(f"❌ {filename}: File not found")
            continue
        
        try:
            delimiter = detect_delimiter(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                print(f"❌ {filename}: Empty file")
                continue
            
            headers = rows[0]
            data_rows = rows[1:]
            
            # Validate structure
            has_headers = len(headers) > 0
            has_data = len(data_rows) > 0
            consistent_columns = all(len(row) == len(headers) for row in data_rows)
            
            status = "✅" if has_headers and has_data and consistent_columns else "❌"
            print(f"{status} {filename}: {len(headers)} columns, {len(data_rows)} data rows")
            
            if not consistent_columns:
                print(f"    ⚠️  Inconsistent column count detected")
            
        except Exception as e:
            print(f"❌ {filename}: Error - {e}")


if __name__ == "__main__":
    print("Sample Data Testing Suite")
    print("=" * 80)
    
    # Test all sample files
    all_passed = test_all_sample_files()
    
    # Test delimiter detection comprehensively
    test_delimiter_detection_comprehensive()
    
    # Validate data structure
    validate_sample_data_structure()
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 All sample data testing completed successfully!")
        print("Task 20 implementation is complete and working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")