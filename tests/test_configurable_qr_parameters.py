#!/usr/bin/env python3
"""Test configurable QR code parameters functionality"""

import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfigurableQRParameters(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.test_dir)
    
    def test_validate_qr_version(self):
        """Test QR version validation"""
        from generate_qr_codes_gui_loop import validate_qr_version
        
        # Valid versions
        self.assertEqual(validate_qr_version("auto"), (True, None))
        self.assertEqual(validate_qr_version("AUTO"), (True, None))
        self.assertEqual(validate_qr_version(""), (True, None))
        self.assertEqual(validate_qr_version("1"), (True, 1))
        self.assertEqual(validate_qr_version("40"), (True, 40))
        self.assertEqual(validate_qr_version("20"), (True, 20))
        
        # Invalid versions
        valid, msg = validate_qr_version("0")
        self.assertFalse(valid)
        self.assertIn("between 1 and 40", msg)
        
        valid, msg = validate_qr_version("41")
        self.assertFalse(valid)
        self.assertIn("between 1 and 40", msg)
        
        valid, msg = validate_qr_version("abc")
        self.assertFalse(valid)
        self.assertIn("must be a number", msg)
    
    def test_validate_error_correction(self):
        """Test error correction validation"""
        from generate_qr_codes_gui_loop import validate_error_correction
        
        # Valid levels
        self.assertEqual(validate_error_correction("L"), (True, "L"))
        self.assertEqual(validate_error_correction("M"), (True, "M"))
        self.assertEqual(validate_error_correction("Q"), (True, "Q"))
        self.assertEqual(validate_error_correction("H"), (True, "H"))
        self.assertEqual(validate_error_correction("l"), (True, "L"))  # Case insensitive
        
        # Invalid levels
        valid, msg = validate_error_correction("")
        self.assertFalse(valid)
        self.assertIn("cannot be empty", msg)
        
        valid, msg = validate_error_correction("X")
        self.assertFalse(valid)
        self.assertIn("must be one of", msg)
    
    def test_get_error_correction_level(self):
        """Test error correction level conversion"""
        import qrcode.constants
        from generate_qr_codes_gui_loop import get_error_correction_level
        
        self.assertEqual(get_error_correction_level("L"), qrcode.constants.ERROR_CORRECT_L)
        self.assertEqual(get_error_correction_level("M"), qrcode.constants.ERROR_CORRECT_M)
        self.assertEqual(get_error_correction_level("Q"), qrcode.constants.ERROR_CORRECT_Q)
        self.assertEqual(get_error_correction_level("H"), qrcode.constants.ERROR_CORRECT_H)
        self.assertEqual(get_error_correction_level("l"), qrcode.constants.ERROR_CORRECT_L)  # Case insensitive
        
        # Default to L for invalid input
        self.assertEqual(get_error_correction_level("X"), qrcode.constants.ERROR_CORRECT_L)
    
    @patch('qrcode.QRCode')
    @patch('os.makedirs')
    def test_custom_qr_parameters_manual_mode(self, mock_makedirs, mock_qr):
        """Test that custom QR parameters are used in manual mode"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Mock QR code generation
        mock_img = mock_qr.return_value.make_image.return_value
        mock_img.save = lambda x: None
        
        create_qr_codes(
            "10", "500", "26.12.31", "#FF0000", self.test_dir, "png", 1,
            security_code="TEST", suffix_code="123",
            qr_version=5, error_correction="H", box_size=20, border=2
        )
        
        # Verify QRCode was called with custom parameters
        import qrcode.constants
        mock_qr.assert_called_with(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=2
        )
    
    @patch('qrcode.QRCode')
    @patch('os.makedirs')
    def test_custom_qr_parameters_csv_mode(self, mock_makedirs, mock_qr):
        """Test that custom QR parameters are used in CSV mode"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Mock QR code generation
        mock_img = mock_qr.return_value.make_image.return_value
        mock_img.save = lambda x: None
        
        csv_data = [["https://example.com"]]
        
        create_qr_codes(
            None, None, None, "#0000FF", self.test_dir, "png", None,
            csv_data=csv_data, input_column=0,
            qr_version=3, error_correction="M", box_size=15, border=1
        )
        
        # Verify QRCode was called with custom parameters
        import qrcode.constants
        mock_qr.assert_called_with(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=15,
            border=1
        )
    
    @patch('qrcode.QRCode')
    @patch('os.makedirs')
    def test_default_qr_parameters(self, mock_makedirs, mock_qr):
        """Test that default QR parameters are used when not specified"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Mock QR code generation
        mock_img = mock_qr.return_value.make_image.return_value
        mock_img.save = lambda x: None
        
        create_qr_codes(
            "5", "100", "26.12.31", "#000000", self.test_dir, "png", 1
        )
        
        # Verify QRCode was called with default parameters
        import qrcode.constants
        mock_qr.assert_called_with(
            version=None,           # Default: auto-sizing
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Default: L
            box_size=10,           # Default: 10
            border=4               # Default: 4
        )
    
    def test_qr_parameter_integration(self):
        """Test QR parameter integration with actual QR generation"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test with custom parameters - should generate QR codes successfully
        create_qr_codes(
            "3", "75", "26.12.31", "#800080", self.test_dir, "png", 1,
            security_code="INTEG", suffix_code="TEST",
            qr_version=2, error_correction="Q", box_size=8, border=3
        )
        
        # Verify file was created
        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.png'))
    
    def test_qr_parameter_edge_cases(self):
        """Test edge cases for QR parameters"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test with minimum and maximum values
        create_qr_codes(
            "1", "1", "01.01.00", "#000000", self.test_dir, "svg", 1,
            qr_version=1, error_correction="H", box_size=1, border=0
        )
        
        # Verify file was created
        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.svg'))

if __name__ == '__main__':
    unittest.main()