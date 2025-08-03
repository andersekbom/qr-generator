#!/usr/bin/env python3
"""Test progress bar functionality"""

import sys
import os
import unittest
import tempfile
import shutil

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestProgressBar(unittest.TestCase):
    
    def test_manual_mode_progress_bar(self):
        """Test progress bar in manual mode with actual QR generation"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Create temporary directory for test
        test_dir = tempfile.mkdtemp()
        
        try:
            # Test manual mode with progress bar (you'll see progress output during test)
            create_qr_codes(
                "5", "100", "26.12.31", "#000000", test_dir, "png", 2,
                security_code="TEST", suffix_code="123"
            )
            
            # Verify files were created
            files = os.listdir(test_dir)
            self.assertEqual(len(files), 2)
            for f in files:
                self.assertTrue(f.endswith('.png'))
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(test_dir)
    
    def test_csv_mode_progress_bar(self):
        """Test progress bar in CSV mode with actual QR generation"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Create temporary directory for test
        test_dir = tempfile.mkdtemp()
        
        try:
            # Test CSV mode with progress bar (you'll see progress output during test)
            csv_data = [["https://example.com/1"], ["https://example.com/2"], ["https://example.com/3"]]
            
            create_qr_codes(
                None, None, None, "#0000FF", test_dir, "png", None,
                csv_data=csv_data, input_column=0
            )
            
            # Verify files were created from CSV data
            files = os.listdir(test_dir)
            self.assertEqual(len(files), 3)
            for f in files:
                self.assertTrue(f.endswith('.png'))
            
        finally:
            # Clean up temporary directory
            shutil.rmtree(test_dir)
    
    def test_tqdm_import_available(self):
        """Test that tqdm is properly imported and available"""
        from generate_qr_codes_gui_loop import tqdm
        
        # Verify tqdm is imported and callable
        self.assertTrue(callable(tqdm))
        
        # Test basic tqdm functionality
        test_iterable = [1, 2, 3]
        progress_bar = tqdm(test_iterable, desc="Test")
        
        # Should be able to get length
        self.assertEqual(len(list(progress_bar)), 3)

if __name__ == '__main__':
    unittest.main()