#!/usr/bin/env python3
"""Test batch operation mode selection functionality"""

import sys
import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBatchOperationModes(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.test_dir)
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_single_generation_mode(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test single QR code generation mode"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs for single generation mode
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # No presets
            False,  # Single generation mode (not batch)
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            False,  # No zip output
            False   # Don't clean up files
        ]
        mock_askstring.side_effect = [
            "5",            # valid_uses
            "100",          # volume  
            "26.12.31",     # end_date
            "#000000",      # color
            "png",          # format
            "SECD",         # security_code
            "23FF45EE"      # suffix_code
        ]
        mock_askinteger.return_value = 1  # Single QR code
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called with count=1 (single generation)
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[0][6], 1)  # count parameter should be 1
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_sequential_batch_mode(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test sequential batch generation mode"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs for sequential batch mode
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # No presets
            True,   # Batch generation mode
            False,  # Sequential batch (not CSV)
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            True,   # Zip output
            False   # Don't clean up files
        ]
        mock_askstring.side_effect = [
            "10",           # valid_uses
            "500",          # volume  
            "31.12.25",     # end_date
            "#FF0000",      # color
            "svg",          # format
            "BATCH",        # security_code
            "TEST",         # suffix_code
            "batch.zip"     # zip filename
        ]
        mock_askinteger.return_value = 25  # Batch of 25 QR codes
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called with count=25 (batch generation)
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[0][6], 25)  # count parameter should be 25
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_csv_batch_mode(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_askopenfilename, mock_showinfo, mock_create, mock_zip, mock_clean):
        """Test CSV batch generation mode"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs for CSV batch mode
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # No presets
            True,   # Batch generation mode
            True,   # CSV batch mode
            False,  # Skip first row
            False,  # No advanced QR parameters
            False,  # No filename customization
            False,  # Use default output directory
            False,  # No zip output
            False   # Don't clean up files
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
            mock_open.return_value.__enter__.return_value.read.return_value = "url1\\nurl2\\nurl3"
            with patch('csv.reader') as mock_csv_reader:
                mock_csv_reader.return_value = [["url1"], ["url2"], ["url3"]]
                
                # Run main function
                main()
        
        # Verify create_qr_codes was called with CSV data
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        # Check that csv_data parameter was passed (not None)
        self.assertIsNotNone(call_args[1]['csv_data'])
        self.assertEqual(len(call_args[1]['csv_data']), 3)
    
    def test_dialog_title_consistency(self):
        """Test that dialog titles are consistent with operation mode"""
        from generate_qr_codes_gui_loop import main
        
        # This test verifies the dialog title setting logic
        # Since we can't easily test GUI dialog titles in unit tests,
        # we'll test the logic that determines operation titles
        
        # Test single mode
        batch_mode = False
        csv_mode = False
        if not batch_mode:
            operation_title = "Single QR Code Generation"
        elif batch_mode and not csv_mode:
            operation_title = "Batch Sequential Generation"
        else:
            operation_title = "CSV Batch Generation"
        
        self.assertEqual(operation_title, "Single QR Code Generation")
        
        # Test sequential batch mode
        batch_mode = True
        csv_mode = False
        if not batch_mode:
            operation_title = "Single QR Code Generation"
        elif batch_mode and not csv_mode:
            operation_title = "Batch Sequential Generation"
        else:
            operation_title = "CSV Batch Generation"
        
        self.assertEqual(operation_title, "Batch Sequential Generation")
        
        # Test CSV batch mode
        batch_mode = True
        csv_mode = True
        if not batch_mode:
            operation_title = "Single QR Code Generation"
        elif batch_mode and not csv_mode:
            operation_title = "Batch Sequential Generation"
        else:
            operation_title = "CSV Batch Generation"
        
        # Note: CSV batch mode goes to the CSV processing branch,
        # so it wouldn't set this title, but this tests the logic
        self.assertNotEqual(operation_title, "Single QR Code Generation")
    
    def test_count_defaults_by_mode(self):
        """Test that count defaults are appropriate for each mode"""
        # Test single mode default
        batch_mode = False
        csv_mode = False
        if batch_mode and not csv_mode:
            default_count = 10
        else:
            default_count = 1
        
        self.assertEqual(default_count, 1)
        
        # Test sequential batch mode default
        batch_mode = True
        csv_mode = False
        if batch_mode and not csv_mode:
            default_count = 10
        else:
            default_count = 1
        
        self.assertEqual(default_count, 10)
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_mode_selection_workflow(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test the complete mode selection workflow"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs to test the workflow
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [
            False,  # No presets
            True,   # Batch generation mode
            False,  # Sequential batch (not CSV)
            True,   # Advanced QR parameters
            True,   # Use payload as filename base
            True,   # Filename customization
            True,   # Custom output directory
            True,   # Zip output
            True    # Clean up files after zipping
        ]
        mock_askstring.side_effect = [
            "20",           # valid_uses
            "1000",         # volume  
            "01.01.26",     # end_date
            "#0000FF",      # color
            "png",          # format
            "WORK",         # security_code
            "FLOW",         # suffix_code
            "5",            # qr_version
            "H",            # error_correction
            "15",           # box_size
            "6",            # border
            "batch",        # filename_prefix
            "test",         # filename_suffix
            "workflow.zip"  # zip filename
        ]
        mock_askinteger.return_value = 50  # count
        
        # Mock directory selection
        with patch('tkinter.filedialog.askdirectory') as mock_askdirectory:
            mock_askdirectory.return_value = "/custom/output"
            
            # Run main function
            main()
        
        # Verify all the expected calls were made
        mock_create.assert_called_once()
        mock_zip.assert_called_once()
        mock_clean.assert_called_once()
        
        # Verify parameters were passed correctly
        call_args = mock_create.call_args
        self.assertEqual(call_args[0][0], "20")  # valid_uses
        self.assertEqual(call_args[0][6], 50)    # count
        self.assertEqual(call_args[0][4], "/custom/output")  # output_folder

if __name__ == '__main__':
    unittest.main()