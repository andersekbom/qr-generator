#!/usr/bin/env python3
"""Test output directory selection functionality"""

import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestOutputDirectorySelection(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directories for testing"""
        self.test_dir1 = tempfile.mkdtemp()
        self.test_dir2 = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directories"""
        shutil.rmtree(self.test_dir1)
        shutil.rmtree(self.test_dir2)
    
    def test_output_directory_integration(self):
        """Test output directory selection with actual file creation"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test that files are created in the specified output directory
        create_qr_codes(
            "3", "50", "26.12.31", "#000000", self.test_dir1, "png", 1,
            security_code="TEST", suffix_code="DIR"
        )
        
        # Verify file was created in the specified directory
        files = os.listdir(self.test_dir1)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.png'))
        
        # Test with different directory
        create_qr_codes(
            "5", "100", "27.12.31", "#FF0000", self.test_dir2, "svg", 2,
            security_code="TEST", suffix_code="DIR2"
        )
        
        # Verify files were created in the second directory
        files2 = os.listdir(self.test_dir2)
        self.assertEqual(len(files2), 2)
        for f in files2:
            self.assertTrue(f.endswith('.svg'))
        
        # Original directory should still have only 1 file
        files1 = os.listdir(self.test_dir1)
        self.assertEqual(len(files1), 1)
    
    def test_csv_mode_custom_output_directory(self):
        """Test CSV mode with custom output directory"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        csv_data = [["https://example.com/1"], ["https://example.com/2"]]
        
        create_qr_codes(
            None, None, None, "#00FF00", self.test_dir1, "png", None,
            csv_data=csv_data, input_column=0
        )
        
        # Verify files were created in the specified directory
        files = os.listdir(self.test_dir1)
        self.assertEqual(len(files), 2)
        for f in files:
            self.assertTrue(f.endswith('.png'))
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.filedialog.askdirectory')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_manual_mode_custom_directory_gui(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_askdirectory, mock_create, mock_zip, mock_clean):
        """Test manual mode GUI with custom output directory"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # Manual mode (not CSV)
            False,  # No advanced QR parameters
            True,   # Use custom output directory
            True    # Zip output
        ]
        mock_askstring.side_effect = [
            "10",           # valid_uses
            "250",          # volume  
            "26.12.31",     # end_date
            "#FF0000",      # color
            "png",          # format
            "SECD",         # security_code
            "23FF45EE",     # suffix_code
            "test.zip"      # zip_file_name
        ]
        mock_askinteger.return_value = 3  # count
        mock_askdirectory.return_value = "/custom/output/path"
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called with custom output directory
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[0][4], "/custom/output/path")  # output_folder parameter
        
        # Verify directory dialog was called
        mock_askdirectory.assert_called_once_with(title="Select Output Directory")
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.filedialog.askdirectory')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_no_directory_selected_fallback(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_askdirectory, mock_showinfo, mock_create, mock_zip, mock_clean):
        """Test fallback to default directory when no directory is selected"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # Manual mode (not CSV)
            False,  # No advanced QR parameters
            True,   # Use custom output directory
            False   # No zip output
        ]
        mock_askstring.side_effect = [
            "5",            # valid_uses
            "100",          # volume  
            "25.12.31",     # end_date
            "#0000FF",      # color
            "svg",          # format
            "TEST",         # security_code
            "CODE"          # suffix_code
        ]
        mock_askinteger.return_value = 1  # count
        mock_askdirectory.return_value = ""  # No directory selected
        
        # Run main function
        main()
        
        # Verify fallback message was shown
        mock_showinfo.assert_called_with("Info", "No directory selected. Using default 'output' folder.")
        
        # Verify create_qr_codes was called with default output directory
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[0][4], "output")  # output_folder parameter
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_default_directory_option(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test choosing default directory option"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # Manual mode (not CSV)
            False,  # No advanced QR parameters
            False,  # Use default output directory
            False   # No zip output
        ]
        mock_askstring.side_effect = [
            "2",            # valid_uses
            "50",           # volume  
            "24.12.31",     # end_date
            "#00FFFF",      # color
            "png",          # format
            "DEFAULT",      # security_code
            "DIR"           # suffix_code
        ]
        mock_askinteger.return_value = 1  # count
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called with default output directory
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[0][4], "output")  # output_folder parameter
    
    def test_directory_creation(self):
        """Test that output directory is created if it doesn't exist"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Create a path that doesn't exist yet
        non_existent_dir = os.path.join(self.test_dir1, "nested", "path")
        
        # Should create the directory and generate files
        create_qr_codes(
            "1", "25", "26.12.31", "#FFFF00", non_existent_dir, "png", 1,
            security_code="CREATE", suffix_code="DIR"
        )
        
        # Verify directory was created and file exists
        self.assertTrue(os.path.exists(non_existent_dir))
        files = os.listdir(non_existent_dir)
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.png'))

if __name__ == '__main__':
    unittest.main()