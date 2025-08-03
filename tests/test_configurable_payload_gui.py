#!/usr/bin/env python3
"""Test configurable payload format in GUI workflow"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestConfigurablePayloadGUI(unittest.TestCase):
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_manual_mode_with_custom_payload(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test manual mode with custom security and suffix codes"""
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
            "MYSEC",        # security_code
            "ABCD123",      # suffix_code
            "test.zip"      # zip_file_name
        ]
        mock_askinteger.return_value = 5  # count
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called with custom parameters
        mock_create.assert_called_once_with(
            "15", "500", "26.12.31", "#FF0000", "output", "png", 5,
            security_code="MYSEC", suffix_code="ABCD123"
        )
        
        # Verify other functions were called
        mock_zip.assert_called_once_with("output", "test.zip", "png")
        mock_clean.assert_called_once_with("output")
    
    @patch('generate_qr_codes_gui_loop.clean_output_folder')
    @patch('generate_qr_codes_gui_loop.zip_output_files')  
    @patch('generate_qr_codes_gui_loop.create_qr_codes')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_default_payload_values(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_create, mock_zip, mock_clean):
        """Test that default payload values are used when user accepts defaults"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.side_effect = [False, False]  # Manual mode, no zip output
        mock_askstring.side_effect = [
            "10",           # valid_uses
            "250",          # volume  
            "27.12.31",     # end_date
            "#000000",      # color
            "svg",          # format
            "SECD",         # security_code (default)
            "23FF45EE"      # suffix_code (default)
        ]
        mock_askinteger.return_value = 3  # count
        
        # Run main function
        main()
        
        # Verify create_qr_codes was called with default security codes
        mock_create.assert_called_once_with(
            "10", "250", "27.12.31", "#000000", "output", "svg", 3,
            security_code="SECD", suffix_code="23FF45EE"
        )
        
        # Verify zip was not called (no zip output)
        mock_zip.assert_called_once_with("output", None, "svg")
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_empty_security_code_error(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test error handling when security code is empty"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = False  # Manual mode
        mock_askstring.side_effect = [
            "5",            # valid_uses
            "100",          # volume  
            "25.12.31",     # end_date
            "#0000FF",      # color
            "png",          # format
            ""              # empty security_code
        ]
        mock_askinteger.return_value = 1  # count
        
        # Run main function
        main()
        
        # Verify error message was shown
        mock_showerror.assert_called_with("Error", "No security code entered. Exiting.")
    
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.Tk')
    def test_empty_suffix_code_error(self, mock_tk, mock_askyesno, mock_askinteger, mock_askstring, mock_showerror):
        """Test error handling when suffix code is empty"""
        from generate_qr_codes_gui_loop import main
        
        # Mock the GUI dialogs
        mock_tk.return_value.withdraw = MagicMock()
        mock_askyesno.return_value = False  # Manual mode
        mock_askstring.side_effect = [
            "8",            # valid_uses
            "200",          # volume  
            "29.12.31",     # end_date
            "#00FF00",      # color
            "svg",          # format
            "VALID",        # security_code
            ""              # empty suffix_code
        ]
        mock_askinteger.return_value = 2  # count
        
        # Run main function
        main()
        
        # Verify error message was shown
        mock_showerror.assert_called_with("Error", "No suffix code entered. Exiting.")

if __name__ == '__main__':
    unittest.main()