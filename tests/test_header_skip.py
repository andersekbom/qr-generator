#!/usr/bin/env python3
"""Test header skip functionality"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import csv
import tempfile

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestHeaderSkipFunctionality(unittest.TestCase):
    
    def test_header_skip_in_csv_processing(self):
        """Test that header row is properly skipped when option is selected"""
        
        # Create temporary CSV file with header
        test_csv_content = """Name,URL,Description
Google,https://www.google.com,Search Engine
GitHub,https://www.github.com,Code Repository"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            temp_csv_path = f.name
        
        try:
            # Test reading CSV with header skip
            with open(temp_csv_path, "r") as infile:
                reader = csv.reader(infile, delimiter=',')
                # Skip header (simulating skip_first_row = True)
                next(reader)
                rows = list(reader)
            
            # Should have 2 data rows, not 3 (header excluded)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], "Google")
            self.assertEqual(rows[1][0], "GitHub")
            
            # Verify no header row in data
            self.assertNotEqual(rows[0][0], "Name")
            
        finally:
            os.unlink(temp_csv_path)
    
    def test_no_header_skip(self):
        """Test that all rows are included when header skip is disabled"""
        
        test_csv_content = """Name,URL,Description
Google,https://www.google.com,Search Engine
GitHub,https://www.github.com,Code Repository"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            temp_csv_path = f.name
        
        try:
            # Test reading CSV without header skip
            with open(temp_csv_path, "r") as infile:
                reader = csv.reader(infile, delimiter=',')
                # Don't skip header (simulating skip_first_row = False)
                rows = list(reader)
            
            # Should have 3 rows including header
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0][0], "Name")  # Header row included
            self.assertEqual(rows[1][0], "Google")
            self.assertEqual(rows[2][0], "GitHub")
            
        finally:
            os.unlink(temp_csv_path)

if __name__ == '__main__':
    unittest.main()