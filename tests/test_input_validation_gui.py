#!/usr/bin/env python3
"""Test input validation in GUI workflow"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestInputValidationGUI(unittest.TestCase):
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_invalid_valid_uses_validation(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test that invalid valid_uses input shows error"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = False  # Manual mode
        mock_askstring.side_effect = [
            "abc",  # Invalid valid_uses (non-numeric)
        ]
        
        # Run main function
        main()
        
        # Verify error message was shown
        mock_showerror.assert_called_with("Validation Error", "Valid uses must be a valid number")
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_invalid_date_format_validation(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test that invalid date format shows error"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = False  # Manual mode
        mock_askstring.side_effect = [
            "15",           # valid_uses
            "500",          # volume
            "2024-12-31",   # Invalid date format (should be DD.MM.YY)
        ]
        
        # Run main function
        main()
        
        # Verify error message was shown
        mock_showerror.assert_called_with("Validation Error", "Date must be in DD.MM.YY format (e.g., 26.12.31)")
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_invalid_color_validation(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test that invalid color format shows error"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = False  # Manual mode
        mock_askstring.side_effect = [
            "10",           # valid_uses
            "250",          # volume
            "26.12.31",     # end_date
            "#GGG",         # Invalid hex color
        ]
        
        # Run main function
        main()
        
        # Verify error message was shown
        mock_showerror.assert_called_with("Validation Error", "Invalid hex color format")
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_invalid_format_validation(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test that invalid format shows error"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = False  # Manual mode
        mock_askstring.side_effect = [
            "5",            # valid_uses
            "100",          # volume
            "27.12.31",     # end_date
            "#FF0000",      # color
            "jpg",          # Invalid format
        ]
        
        # Run main function
        main()
        
        # Verify error message was shown
        mock_showerror.assert_called_with("Validation Error", "Format must be one of: png, svg")
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_csv_mode_validation(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test validation in CSV mode"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = True  # CSV mode
        mock_askstring.side_effect = [
            ",",            # delimiter
            "gif",          # Invalid format
        ]
        mock_askinteger.return_value = 0  # input_column
        
        # Run main function (will fail at file selection first, but we're testing validation flow)
        main()
        
        # The function should exit early due to no file selected, not reaching format validation
        # This test verifies CSV mode path doesn't break
        mock_showerror.assert_called_with("Error", "No file selected. Exiting.")
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_valid_inputs_pass_validation(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test that valid inputs pass validation and continue processing"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [False, True]  # Manual mode, zip output
        mock_askstring.side_effect = [
            "15",           # valid_uses
            "500",          # volume  
            "26.12.31",     # end_date
            "#FF0000",      # color
            "png",          # format
            "SECD",         # security_code
            "23FF45EE",     # suffix_code
            "test.zip"      # zip_file_name
        ]
        mock_askinteger.return_value = 5  # count
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called (validation passed)
        mock_create.assert_called_once_with(
            "15", "500", "26.12.31", "#FF0000", "output", "png", 5,
            security_code="SECD", suffix_code="23FF45EE"
        )

if __name__ == '__main__':
    unittest.main()