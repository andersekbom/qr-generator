#!/usr/bin/env python3
"""Test filename customization functionality"""

import sys
import os
import unittest
import tempfile
import shutil

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFilenameCustomization(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.test_dir)
    
    def test_generate_custom_filename_default(self):
        """Test default filename generation"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        # Test with payload as base
        result = generate_custom_filename("M-10-00000001-500-26.12.31-SECD-23FF45EE")
        self.assertEqual(result, "M-10-00000001-500-26.12.31-SECD-23FF45EE")
        
        # Test with URL payload
        result = generate_custom_filename("https://example.com/test?id=123")
        self.assertEqual(result, "httpsexample.comtestid123")
        
        # Test with empty payload
        result = generate_custom_filename("", index=5)
        self.assertEqual(result, "qr_code_5")
    
    def test_generate_custom_filename_with_prefix(self):
        """Test filename generation with prefix"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        result = generate_custom_filename("test_payload", prefix="PREFIX")
        self.assertEqual(result, "PREFIX_test_payload")
        
        result = generate_custom_filename("", prefix="EMPTY", index=3)
        self.assertEqual(result, "EMPTY_qr_code_3")
    
    def test_generate_custom_filename_with_suffix(self):
        """Test filename generation with suffix"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        result = generate_custom_filename("test_payload", suffix="SUFFIX")
        self.assertEqual(result, "test_payload_SUFFIX")
        
        result = generate_custom_filename("", suffix="END", index=7)
        self.assertEqual(result, "qr_code_7_END")
    
    def test_generate_custom_filename_with_prefix_and_suffix(self):
        """Test filename generation with both prefix and suffix"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        result = generate_custom_filename("middle", prefix="START", suffix="END")
        self.assertEqual(result, "START_middle_END")
        
        result = generate_custom_filename("", prefix="A", suffix="Z", index=1)
        self.assertEqual(result, "A_qr_code_1_Z")
    
    def test_generate_custom_filename_index_based(self):
        """Test index-based filename generation"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        # Test with use_payload_as_base=False
        result = generate_custom_filename("ignore_this", use_payload_as_base=False, index=10)
        self.assertEqual(result, "qr_code_10")
        
        result = generate_custom_filename("also_ignore", prefix="TEST", suffix="NUM", use_payload_as_base=False, index=42)
        self.assertEqual(result, "TEST_qr_code_42_NUM")
    
    def test_filename_customization_manual_mode(self):
        """Test filename customization in manual mode"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test with prefix and suffix
        create_qr_codes(
            "5", "100", "26.12.31", "#000000", self.test_dir, "png", 2,
            security_code="TEST", suffix_code="FILE",
            filename_prefix="PREFIX", filename_suffix="SUFFIX"
        )
        
        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 2)
        
        # Check that filenames have prefix and suffix
        for f in files:
            self.assertTrue(f.startswith("PREFIX_"))
            self.assertTrue("_SUFFIX" in f)
            self.assertTrue(f.endswith(".png"))
    
    def test_filename_customization_csv_mode(self):
        """Test filename customization in CSV mode"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        csv_data = [["url1"], ["url2"], ["url3"]]
        
        # Test with prefix and suffix using payload as base
        create_qr_codes(
            None, None, None, "#FF0000", self.test_dir, "png", None,
            csv_data=csv_data, input_column=0,
            filename_prefix="CSV", filename_suffix="DATA", use_payload_as_filename=True
        )
        
        files = os.listdir(self.test_dir)
        self.assertEqual(len(files), 3)
        
        # Check filename format
        for f in files:
            self.assertTrue(f.startswith("CSV_"))
            self.assertTrue("_DATA" in f)
            self.assertTrue(f.endswith(".png"))
    
    def test_filename_customization_csv_index_based(self):
        """Test CSV mode with index-based filenames"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        csv_data = [["https://example.com/1"], ["https://example.com/2"]]
        
        # Test with use_payload_as_filename=False
        create_qr_codes(
            None, None, None, "#00FF00", self.test_dir, "svg", None,
            csv_data=csv_data, input_column=0,
            filename_prefix="IDX", filename_suffix="NUM", use_payload_as_filename=False
        )
        
        files = sorted(os.listdir(self.test_dir))
        self.assertEqual(len(files), 2)
        
        # Check index-based naming
        expected_files = ["IDX_qr_code_1_NUM.svg", "IDX_qr_code_2_NUM.svg"]
        self.assertEqual(files, expected_files)
    
    def test_filename_special_characters_cleanup(self):
        """Test that special characters are cleaned from filenames"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        # Test with special characters
        result = generate_custom_filename("test@#$%^&*()+={}[]|\\:;\"'<>?,./")
        self.assertEqual(result, "test")
        
        # Test with mixed characters
        result = generate_custom_filename("hello-world_123.txt test")
        self.assertEqual(result, "hello-world_123.txt test")
        
        # Test with only special characters (should fall back to index)
        result = generate_custom_filename("@#$%^&*()", index=99)
        self.assertEqual(result, "qr_code_99")
    
    def test_filename_customization_integration(self):
        """Test filename customization integration with actual file creation"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test comprehensive customization
        create_qr_codes(
            "3", "75", "28.12.31", "#800080", self.test_dir, "svg", 3,
            security_code="CUSTOM", suffix_code="NAME",
            filename_prefix="PROJECT", filename_suffix="V1", use_payload_as_filename=False
        )
        
        files = sorted(os.listdir(self.test_dir))
        self.assertEqual(len(files), 3)
        
        expected_files = [
            "PROJECT_qr_code_1_V1.svg",
            "PROJECT_qr_code_2_V1.svg", 
            "PROJECT_qr_code_3_V1.svg"
        ]
        self.assertEqual(files, expected_files)
    
    def test_empty_prefix_suffix_handling(self):
        """Test handling of empty prefix/suffix values"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        # Test empty prefix
        result = generate_custom_filename("base", prefix="", suffix="end")
        self.assertEqual(result, "base_end")
        
        # Test empty suffix
        result = generate_custom_filename("base", prefix="start", suffix="")
        self.assertEqual(result, "start_base")
        
        # Test both empty
        result = generate_custom_filename("base", prefix="", suffix="")
        self.assertEqual(result, "base")
    
    def test_long_filename_handling(self):
        """Test handling of very long filenames"""
        from generate_qr_codes_gui_loop import generate_custom_filename
        
        # Test with very long payload
        long_payload = "a" * 200
        result = generate_custom_filename(long_payload, prefix="SHORT", suffix="END")
        
        # Should still work (filesystem limits will apply at file creation)
        self.assertTrue(result.startswith("SHORT_"))
        self.assertTrue(result.endswith("_END"))
        self.assertIn("a" * 200, result)

if __name__ == '__main__':
    unittest.main()