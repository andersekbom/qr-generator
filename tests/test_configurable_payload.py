#!/usr/bin/env python3
"""Test configurable payload format functionality"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfigurablePayload(unittest.TestCase):
    
    def test_default_payload_format(self):
        """Test that default payload format uses SECD and 23FF45EE"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses="5", volume="100", end_date="26.12.31",
                color="#000000", output_folder="test", format="png", count=1
            )
            
            # Check that add_data was called with default format
            call_args = mock_qr.return_value.add_data.call_args
            payload = call_args[0][0]
            self.assertIn("-SECD-", payload)
            self.assertIn("-23FF45EE", payload)
            self.assertEqual(payload, "M-5-00000001-100-26.12.31-SECD-23FF45EE")
    
    def test_custom_payload_format(self):
        """Test that custom security and suffix codes are used"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses="10", volume="250", end_date="27.12.31",
                color="#FF0000", output_folder="test", format="png", count=2,
                security_code="CUSTOM", suffix_code="ABCD1234"
            )
            
            # Check first QR code payload
            calls = mock_qr.return_value.add_data.call_args_list
            self.assertEqual(len(calls), 2)
            
            payload1 = calls[0][0][0]
            payload2 = calls[1][0][0]
            
            self.assertEqual(payload1, "M-10-00000001-250-27.12.31-CUSTOM-ABCD1234")
            self.assertEqual(payload2, "M-10-00000002-250-27.12.31-CUSTOM-ABCD1234")
    
    def test_empty_security_codes(self):
        """Test behavior with empty security codes"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses="1", volume="50", end_date="25.12.31",
                color="#0000FF", output_folder="test", format="png", count=1,
                security_code="", suffix_code=""
            )
            
            # Check payload format with empty codes
            call_args = mock_qr.return_value.add_data.call_args
            payload = call_args[0][0]
            self.assertEqual(payload, "M-1-00000001-50-25.12.31--")
    
    def test_special_character_codes(self):
        """Test security codes with special characters"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses="3", volume="75", end_date="28.12.31",
                color="#00FF00", output_folder="test", format="png", count=1,
                security_code="SEC@123", suffix_code="XYZ#456"
            )
            
            # Check payload with special characters
            call_args = mock_qr.return_value.add_data.call_args
            payload = call_args[0][0]
            self.assertEqual(payload, "M-3-00000001-75-28.12.31-SEC@123-XYZ#456")
    
    def test_csv_mode_ignores_payload_format(self):
        """Test that CSV mode doesn't use the sequential payload format"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        test_data = [
            ["https://example.com/1"],
            ["https://example.com/2"]
        ]
        
        with patch('os.makedirs'), patch('qrcode.QRCode') as mock_qr:
            mock_img = mock_qr.return_value.make_image.return_value
            mock_img.save = lambda x: None
            
            create_qr_codes(
                valid_uses=None, volume=None, end_date=None,
                color="#000000", output_folder="test", format="png", count=None,
                csv_data=test_data, input_column=0,
                security_code="SHOULD_NOT_APPEAR", suffix_code="IGNORE_ME"
            )
            
            # Check that CSV data is used directly, not payload format
            calls = mock_qr.return_value.add_data.call_args_list
            self.assertEqual(len(calls), 2)
            
            payload1 = calls[0][0][0]
            payload2 = calls[1][0][0]
            
            self.assertEqual(payload1, "https://example.com/1")
            self.assertEqual(payload2, "https://example.com/2")
            
            # Security codes should not appear in CSV mode
            self.assertNotIn("SHOULD_NOT_APPEAR", payload1)
            self.assertNotIn("IGNORE_ME", payload1)

if __name__ == '__main__':
    unittest.main()