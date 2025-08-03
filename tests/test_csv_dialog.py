#!/usr/bin/env python3
"""Test script for CSV file selection dialog"""

import sys
import os
import tempfile

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csv_dialog():
    """
    Manual test for CSV dialog functionality.
    This test requires user interaction to verify the dialog behavior.
    """
    print("Testing CSV file selection dialog:")
    print("-" * 40)
    print("1. This will open the QR generator application")
    print("2. You should see a dialog asking about input mode")
    print("3. Test both 'Yes' (CSV) and 'No' (Manual) options")
    print("4. If you select 'Yes', a file dialog should appear")
    print("5. Close the application after testing")
    print("\nStarting application...")
    
    # Create a sample CSV file for testing
    sample_csv = """data
https://example.com/1
https://example.com/2
https://example.com/3"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_csv)
        temp_csv = f.name
    
    print(f"\nSample CSV file created: {temp_csv}")
    print("You can use this file to test the CSV file selection dialog.")
    
    try:
        from generate_qr_codes_gui_loop import main
        main()
    except Exception as e:
        print(f"Error running application: {e}")
    finally:
        # Clean up
        try:
            os.unlink(temp_csv)
            print(f"\nCleaned up test file: {temp_csv}")
        except:
            pass

if __name__ == "__main__":
    test_csv_dialog()