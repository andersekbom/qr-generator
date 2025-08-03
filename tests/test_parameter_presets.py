#!/usr/bin/env python3
"""Test parameter preset saving/loading functionality"""

import sys
import os
import unittest
import tempfile
import shutil
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestParameterPresets(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test presets"""
        self.test_dir = tempfile.mkdtemp()
        self.original_getcwd = os.getcwd
        # Mock os.getcwd to return our test directory
        os.getcwd = lambda: self.test_dir
    
    def tearDown(self):
        """Clean up temporary files and restore os.getcwd"""
        os.getcwd = self.original_getcwd
        shutil.rmtree(self.test_dir)
    
    def test_get_presets_dir(self):
        """Test presets directory creation"""
        from generate_qr_codes_gui_loop import get_presets_dir
        
        presets_dir = get_presets_dir()
        expected_dir = os.path.join(self.test_dir, "presets")
        
        self.assertEqual(presets_dir, expected_dir)
        self.assertTrue(os.path.exists(presets_dir))
        self.assertTrue(os.path.isdir(presets_dir))
    
    def test_save_preset_success(self):
        """Test successful preset saving"""
        from generate_qr_codes_gui_loop import save_preset
        
        test_params = {
            "mode": "manual",
            "valid_uses": "10",
            "volume": "500",
            "end_date": "26.12.31",
            "color": "#FF0000",
            "format": "png"
        }
        
        success, message = save_preset("test_preset", test_params)
        
        self.assertTrue(success)
        self.assertIn("test_preset", message)
        self.assertIn("saved successfully", message)
        
        # Verify file was created
        preset_file = os.path.join(self.test_dir, "presets", "test_preset.json")
        self.assertTrue(os.path.exists(preset_file))
        
        # Verify content
        with open(preset_file, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_params)
    
    def test_load_preset_success(self):
        """Test successful preset loading"""
        from generate_qr_codes_gui_loop import save_preset, load_preset
        
        test_params = {
            "mode": "csv",
            "format": "svg",
            "color": "#00FF00",
            "delimiter": ";",
            "input_column": 1
        }
        
        # First save the preset
        save_preset("load_test", test_params)
        
        # Then load it
        success, loaded_params = load_preset("load_test")
        
        self.assertTrue(success)
        self.assertEqual(loaded_params, test_params)
    
    def test_load_preset_not_found(self):
        """Test loading non-existent preset"""
        from generate_qr_codes_gui_loop import load_preset
        
        success, message = load_preset("nonexistent")
        
        self.assertFalse(success)
        self.assertIn("not found", message)
    
    def test_list_presets_empty(self):
        """Test listing presets when none exist"""
        from generate_qr_codes_gui_loop import list_presets
        
        presets = list_presets()
        self.assertEqual(presets, [])
    
    def test_list_presets_with_data(self):
        """Test listing presets when some exist"""
        from generate_qr_codes_gui_loop import save_preset, list_presets
        
        # Save multiple presets
        save_preset("preset1", {"mode": "manual"})
        save_preset("preset2", {"mode": "csv"})
        save_preset("preset3", {"mode": "manual"})
        
        presets = list_presets()
        
        self.assertEqual(len(presets), 3)
        self.assertIn("preset1", presets)
        self.assertIn("preset2", presets)
        self.assertIn("preset3", presets)
    
    def test_delete_preset_success(self):
        """Test successful preset deletion"""
        from generate_qr_codes_gui_loop import save_preset, delete_preset, list_presets
        
        # Save a preset first
        save_preset("delete_me", {"mode": "manual"})
        self.assertIn("delete_me", list_presets())
        
        # Delete it
        success, message = delete_preset("delete_me")
        
        self.assertTrue(success)
        self.assertIn("delete_me", message)
        self.assertIn("deleted successfully", message)
        
        # Verify it's gone
        self.assertNotIn("delete_me", list_presets())
    
    def test_delete_preset_not_found(self):
        """Test deleting non-existent preset"""
        from generate_qr_codes_gui_loop import delete_preset
        
        success, message = delete_preset("nonexistent")
        
        self.assertFalse(success)
        self.assertIn("not found", message)
    
    def test_create_manual_mode_preset(self):
        """Test creating manual mode preset dictionary"""
        from generate_qr_codes_gui_loop import create_manual_mode_preset
        
        preset = create_manual_mode_preset(
            "15", "1000", "31.12.25", "#123456", "svg", "TEST", "CODE",
            qr_version=10, error_correction="H", box_size=15, border=5,
            filename_prefix="pre", filename_suffix="suf", use_payload_as_filename=False
        )
        
        expected = {
            "mode": "manual",
            "valid_uses": "15",
            "volume": "1000",
            "end_date": "31.12.25",
            "color": "#123456",
            "format": "svg",
            "security_code": "TEST",
            "suffix_code": "CODE",
            "qr_version": 10,
            "error_correction": "H",
            "box_size": 15,
            "border": 5,
            "filename_prefix": "pre",
            "filename_suffix": "suf",
            "use_payload_as_filename": False
        }
        
        self.assertEqual(preset, expected)
    
    def test_create_csv_mode_preset(self):
        """Test creating CSV mode preset dictionary"""
        from generate_qr_codes_gui_loop import create_csv_mode_preset
        
        preset = create_csv_mode_preset(
            "png", "#ABCDEF", qr_version=None, error_correction="M", box_size=8, border=3,
            filename_prefix="csv", filename_suffix="data", use_payload_as_filename=True,
            delimiter="|", input_column=2, skip_first_row=True
        )
        
        expected = {
            "mode": "csv",
            "format": "png",
            "color": "#ABCDEF",
            "qr_version": None,
            "error_correction": "M",
            "box_size": 8,
            "border": 3,
            "filename_prefix": "csv",
            "filename_suffix": "data",
            "use_payload_as_filename": True,
            "delimiter": "|",
            "input_column": 2,
            "skip_first_row": True
        }
        
        self.assertEqual(preset, expected)
    
    def test_preset_integration_manual_mode(self):
        """Test preset integration with actual parameter values"""
        from generate_qr_codes_gui_loop import create_manual_mode_preset, save_preset, load_preset
        
        # Create comprehensive preset
        original_params = create_manual_mode_preset(
            "25", "750", "15.06.26", "#FF8800", "svg", "SECURE", "SUFFIX",
            qr_version=5, error_correction="Q", box_size=12, border=2,
            filename_prefix="test", filename_suffix="end", use_payload_as_filename=True
        )
        
        # Save and reload
        save_preset("integration_test", original_params)
        success, loaded_params = load_preset("integration_test")
        
        self.assertTrue(success)
        self.assertEqual(loaded_params, original_params)
        
        # Verify all fields preserved
        self.assertEqual(loaded_params["mode"], "manual")
        self.assertEqual(loaded_params["valid_uses"], "25")
        self.assertEqual(loaded_params["volume"], "750")
        self.assertEqual(loaded_params["qr_version"], 5)
        self.assertEqual(loaded_params["error_correction"], "Q")
    
    def test_preset_integration_csv_mode(self):
        """Test preset integration for CSV mode"""
        from generate_qr_codes_gui_loop import create_csv_mode_preset, save_preset, load_preset
        
        # Create comprehensive CSV preset
        original_params = create_csv_mode_preset(
            "png", "#0088FF", qr_version=20, error_correction="H", box_size=6, border=8,
            filename_prefix="batch", filename_suffix="out", use_payload_as_filename=False,
            delimiter="\t", input_column=3, skip_first_row=False
        )
        
        # Save and reload
        save_preset("csv_integration_test", original_params)
        success, loaded_params = load_preset("csv_integration_test")
        
        self.assertTrue(success)
        self.assertEqual(loaded_params, original_params)
        
        # Verify CSV-specific fields
        self.assertEqual(loaded_params["mode"], "csv")
        self.assertEqual(loaded_params["delimiter"], "\t")
        self.assertEqual(loaded_params["input_column"], 3)
        self.assertEqual(loaded_params["skip_first_row"], False)
    
    def test_save_preset_invalid_characters(self):
        """Test saving preset with special characters in name"""
        from generate_qr_codes_gui_loop import save_preset
        
        test_params = {"mode": "manual", "format": "png"}
        
        # Should still work with most characters
        success, message = save_preset("test@#$preset", test_params)
        self.assertTrue(success)
        
        # Verify file created (filesystem will handle character conversion)
        presets_dir = os.path.join(self.test_dir, "presets")
        files = os.listdir(presets_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.json'))
    
    def test_preset_file_corruption_handling(self):
        """Test handling of corrupted preset files"""
        from generate_qr_codes_gui_loop import load_preset
        
        # Create corrupted preset file
        presets_dir = os.path.join(self.test_dir, "presets")
        os.makedirs(presets_dir, exist_ok=True)
        corrupt_file = os.path.join(presets_dir, "corrupt.json")
        
        with open(corrupt_file, 'w') as f:
            f.write("invalid json content {")
        
        success, message = load_preset("corrupt")
        
        self.assertFalse(success)
        self.assertIn("Failed to load preset", message)

if __name__ == '__main__':
    unittest.main()