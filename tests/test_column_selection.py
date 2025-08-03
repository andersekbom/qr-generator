#!/usr/bin/env python3
"""Test column selection and header skip functionality"""

import sys
import os
import unittest
from unittest.mock import patch, mock_open

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestColumnSelectionAndHeaderSkip(unittest.TestCase):
    
    def test_column_selection_functionality(self):
        """Test that column selection works with multi-column CSV"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test data with multiple columns
        test_data = [
            ["Name", "URL", "Description"],
            ["Google", "https://www.google.com", "Search Engine"],
            ["GitHub", "https://www.github.com", "Code Repository"]
        ]
        
        # Test column 0 (Name)
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses=None, volume=None, end_date=None,
                color="#000000", output_folder="test", format="png",
                count=None, csv_data=test_data[1:], input_column=0
            )
            
            # Verify QR codes were created with column 0 data
            calls = mock_qr.return_value.add_data.call_args_list
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][0][0], "Google")
            self.assertEqual(calls[1][0][0], "GitHub")
    
    def test_different_column_selection(self):
        """Test selecting different columns"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        test_data = [
            ["Google", "https://www.google.com", "Search Engine"],
            ["GitHub", "https://www.github.com", "Code Repository"]
        ]
        
        # Test column 1 (URL)
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses=None, volume=None, end_date=None,
                color="#000000", output_folder="test", format="png",
                count=None, csv_data=test_data, input_column=1
            )
            
            # Verify QR codes were created with column 1 data (URLs)
            calls = mock_qr.return_value.add_data.call_args_list
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][0][0], "https://www.google.com")
            self.assertEqual(calls[1][0][0], "https://www.github.com")
    
    def test_invalid_column_handling(self):
        """Test handling of invalid column selection"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        test_data = [
            ["Google", "https://www.google.com"],  # Only 2 columns
        ]
        
        with patch('os.makedirs'), patch('qrcode.QRCode'), patch('builtins.print') as mock_print:
            create_qr_codes(
                valid_uses=None, volume=None, end_date=None,
                color="#000000", output_folder="test", format="png",
                count=None, csv_data=test_data, input_column=5  # Invalid column
            )
            
            # Should print warning about missing column
            mock_print.assert_called_with("Warning: Row 1 doesn't have column 5, skipping")

if __name__ == '__main__':
    unittest.main()