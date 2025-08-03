#!/usr/bin/env python3
"""Test selective file cleanup functionality"""

import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSelectiveFileCleanup(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.test_dir)
    
    def test_clean_output_folder_function(self):
        """Test the clean_output_folder function directly"""
        from generate_qr_codes_gui_loop import clean_output_folder
        
        # Create test files
        test_files = ["file1.png", "file2.svg", "file3.txt"]
        for filename in test_files:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test content")
        
        # Verify files exist
        self.assertEqual(len(os.listdir(self.test_dir)), 3)
        
        # Clean the folder
        clean_output_folder(self.test_dir)
        
        # Verify files are deleted
        self.assertEqual(len(os.listdir(self.test_dir)), 0)
    
    def test_selective_cleanup_integration_with_files(self):
        """Test selective cleanup with actual file creation and cleanup"""
        from generate_qr_codes_gui_loop import create_qr_codes, clean_output_folder
        
        # Generate some QR codes
        create_qr_codes(
            "2", "50", "26.12.31", "#000000", self.test_dir, "png", 2,
            security_code="CLEAN", suffix_code="TEST"
        )
        
        # Verify files were created
        files_before = os.listdir(self.test_dir)
        self.assertEqual(len(files_before), 2)
        
        # Test cleanup
        clean_output_folder(self.test_dir)
        
        # Verify files were cleaned up
        files_after = os.listdir(self.test_dir)
        self.assertEqual(len(files_after), 0)
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.Tk')
    def test_csv_mode_cleanup_yes_with_zip(self, mock_tk, mock_askinteger, mock_askstring, mock_askopenfilename, mock_showinfo, mock_askyesno, mock_create, mock_zip, mock_clean):
        """Test CSV mode cleanup when user chooses YES to cleanup after zipping"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            True,   # CSV mode
            False,  # Skip first row
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            True,   # Zip output
            True    # Clean up files after zipping
        ]
        mock_askstring.side_effect = [
            ",",            # delimiter
            "png",          # format
            "#000000",      # color
            "test.zip"      # zip filename
        ]
        mock_askinteger.return_value = 0  # input_column
        mock_askopenfilename.return_value = "test.csv"
        
        # Mock CSV file reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "url1,data1\nurl2,data2"
            with patch('csv.reader') as mock_csv_reader:
                mock_csv_reader.return_value = [["url1", "data1"], ["url2", "data2"]]
                
                # Run main function
                main()
        
        # Verify cleanup was called
        mock_clean.assert_called_once_with("output")
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.Tk')
    def test_csv_mode_cleanup_no_with_zip(self, mock_tk, mock_askinteger, mock_askstring, mock_askopenfilename, mock_showinfo, mock_askyesno, mock_create, mock_zip, mock_clean):
        """Test CSV mode cleanup when user chooses NO to cleanup after zipping"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            True,   # CSV mode
            False,  # Skip first row
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            True,   # Zip output
            False   # Don't clean up files after zipping
        ]
        mock_askstring.side_effect = [
            ",",            # delimiter
            "svg",          # format
            "#FF0000",      # color
            "keep.zip"      # zip filename
        ]
        mock_askinteger.return_value = 0  # input_column
        mock_askopenfilename.return_value = "test.csv"
        
        # Mock CSV file reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "url1\nurl2"
            with patch('csv.reader') as mock_csv_reader:
                mock_csv_reader.return_value = [["url1"], ["url2"]]
                
                # Run main function
                main()
        
        # Verify cleanup was NOT called
        mock_clean.assert_not_called()
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.Tk')
    def test_csv_mode_no_zip_cleanup_yes(self, mock_tk, mock_askinteger, mock_askstring, mock_askopenfilename, mock_showinfo, mock_askyesno, mock_create, mock_zip, mock_clean):
        """Test CSV mode cleanup when no zip is created but user chooses YES to cleanup"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            True,   # CSV mode
            False,  # Skip first row
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            False,  # No zip output
            True    # Clean up files anyway
        ]
        mock_askstring.side_effect = [
            ",",            # delimiter
            "png",          # format
            "#00FF00"       # color
        ]
        mock_askinteger.return_value = 0  # input_column
        mock_askopenfilename.return_value = "test.csv"
        
        # Mock CSV file reading
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "url1\nurl2"
            with patch('csv.reader') as mock_csv_reader:
                mock_csv_reader.return_value = [["url1"], ["url2"]]
                
                # Run main function
                main()
        
        # Verify cleanup was called
        mock_clean.assert_called_once_with("output")
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_manual_mode_cleanup_yes_with_zip(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test manual mode cleanup when user chooses YES to cleanup after zipping"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # Manual mode (not CSV)
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            True,   # Zip output
            True    # Clean up files after zipping
        ]
        mock_askstring.side_effect = [
            "10",           # valid_uses
            "250",          # volume  
            "26.12.31",     # end_date
            "#0000FF",      # color
            "png",          # format
            "SECD",         # security_code
            "23FF45EE",     # suffix_code
            "cleanup.zip"   # zip_file_name
        ]
        mock_askinteger.return_value = 3  # count
        
        # Run main function
        main()
        
        # Verify cleanup was called
        mock_clean.assert_called_once_with("output")
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_manual_mode_cleanup_no_with_zip(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test manual mode cleanup when user chooses NO to cleanup after zipping"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # Manual mode (not CSV)
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            True,   # Zip output
            False   # Don't clean up files after zipping
        ]
        mock_askstring.side_effect = [
            "5",            # valid_uses
            "100",          # volume  
            "27.12.31",     # end_date
            "#FF00FF",      # color
            "svg",          # format
            "TEST",         # security_code
            "KEEP",         # suffix_code
            "noClean.zip"   # zip_file_name
        ]
        mock_askinteger.return_value = 2  # count
        
        # Run main function
        main()
        
        # Verify cleanup was NOT called
        mock_clean.assert_not_called()
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_manual_mode_no_zip_cleanup_no(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test manual mode cleanup when no zip is created and user chooses NO to cleanup"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # Manual mode (not CSV)
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            False,  # No zip output
            False   # Don't clean up files
        ]
        mock_askstring.side_effect = [
            "1",            # valid_uses
            "25",           # volume  
            "28.12.31",     # end_date
            "#FFFF00",      # color
            "png",          # format
            "KEEP",         # security_code
            "FILES"         # suffix_code
        ]
        mock_askinteger.return_value = 1  # count
        
        # Run main function
        main()
        
        # Verify cleanup was NOT called
        mock_clean.assert_not_called()
    
    def test_cleanup_with_nested_directories(self):
        """Test cleanup with nested directory structure"""
        from generate_qr_codes_gui_loop import clean_output_folder
        
        # Create nested directory structure with files
        nested_dir = os.path.join(self.test_dir, "subdir")
        os.makedirs(nested_dir)
        
        # Create files in both root and nested directory
        with open(os.path.join(self.test_dir, "root_file.png"), 'w') as f:
            f.write("root content")
        with open(os.path.join(nested_dir, "nested_file.svg"), 'w') as f:
            f.write("nested content")
        
        # Verify files exist
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "root_file.png")))
        self.assertTrue(os.path.exists(os.path.join(nested_dir, "nested_file.svg")))
        
        # Clean the folder
        clean_output_folder(self.test_dir)
        
        # Verify all files are deleted (directories may remain empty)
        for root, dirs, files in os.walk(self.test_dir):
            self.assertEqual(len(files), 0)

if __name__ == '__main__':
    unittest.main()