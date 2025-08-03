#!/usr/bin/env python3
"""Test script for detect_delimiter function"""

import os
import tempfile
from generate_qr_codes_gui_loop import detect_delimiter

def test_detect_delimiter():
    # Test data with different delimiters
    test_cases = [
        ("comma", "name,email,phone\nJohn,john@email.com,123-456-7890\n", ","),
        ("semicolon", "name;email;phone\nJohn;john@email.com;123-456-7890\n", ";"),
        ("tab", "name\temail\tphone\nJohn\tjohn@email.com\t123-456-7890\n", "\t"),
        ("pipe", "name|email|phone\nJohn|john@email.com|123-456-7890\n", "|"),
    ]
    
    print("Testing detect_delimiter function:")
    print("-" * 40)
    
    for name, content, expected_delimiter in test_cases:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            # Test delimiter detection
            detected = detect_delimiter(temp_file)
            status = "✓ PASS" if detected == expected_delimiter else "✗ FAIL"
            print(f"{name:10} | Expected: '{expected_delimiter}' | Detected: '{detected}' | {status}")
        except Exception as e:
            print(f"{name:10} | ERROR: {e}")
        finally:
            # Clean up
            os.unlink(temp_file)

if __name__ == "__main__":
    test_detect_delimiter()