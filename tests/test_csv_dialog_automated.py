#!/usr/bin/env python3
"""Automated test for CSV file selection dialog (no user interaction required)"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCSVDialog(unittest.TestCase):
    
    def setUp(self):
        """Create a sample CSV file for testing"""
        self.sample_csv = """data,description
https://example.com/1,Test URL 1
https://example.com/2,Test URL 2
https://example.com/3,Test URL 3"""
        
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_csv.write(self.sample_csv)
        self.temp_csv.close()
    
    def tearDown(self):
        """Clean up test files"""
        try:
            os.unlink(self.temp_csv.name)
        except:
            pass
    
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    def test_csv_mode_selected(self, mock_askinteger, mock_askstring, mock_showerror, 
                              mock_showinfo, mock_filedialog, mock_askyesno):
        """Test CSV mode selection and file dialog"""
        
        # Mock user selecting CSV mode (Yes)
        mock_askyesno.return_value = True
        # Mock file dialog returning our test CSV
        mock_filedialog.return_value = self.temp_csv.name
        # Mock the info message about CSV not implemented
        mock_showinfo.return_value = None
        
        # Mock manual parameter inputs (fallback) - only 5 needed since zip_output=True triggers zip filename
        mock_askstring.side_effect = ['15', '500', '26.12.31', '#000000', 'png', 'test.zip']
        mock_askinteger.return_value = 1
        
        # Import and patch the main function to avoid actual QR generation
        from generate_qr_codes_gui_loop import main
        
        with patch('generate_qr_codes_gui_loop.create_qr_codes') as mock_create, \
             patch('generate_qr_codes_gui_loop.zip_output_files') as mock_zip, \
             patch('generate_qr_codes_gui_loop.clean_output_folder') as mock_clean, \
             patch('tkinter.Tk') as mock_tk:
            
            # Mock Tk root window
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Run main function
            main()
            
            # Verify CSV mode was selected (askyesno called twice: input mode + zip output)
            self.assertEqual(mock_askyesno.call_count, 2)
            # Verify file dialog was opened
            mock_filedialog.assert_called_once_with(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
            # Verify info message about CSV not implemented was shown
            mock_showinfo.assert_called_once()
            
            print("✓ CSV mode selection works correctly")
            print("✓ File dialog opens when CSV mode selected")
            print("✓ Fallback to manual mode works")
    
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    def test_manual_mode_selected(self, mock_askinteger, mock_askstring, 
                                 mock_showerror, mock_askyesno):
        """Test manual mode selection (No CSV)"""
        
        # Mock user selecting manual mode (No)
        mock_askyesno.return_value = False
        
        # Mock manual parameter inputs - 5 string inputs expected
        mock_askstring.side_effect = ['15', '500', '26.12.31', '#000000', 'png']
        mock_askinteger.return_value = 1
        
        from generate_qr_codes_gui_loop import main
        
        with patch('generate_qr_codes_gui_loop.create_qr_codes') as mock_create, \
             patch('generate_qr_codes_gui_loop.zip_output_files') as mock_zip, \
             patch('generate_qr_codes_gui_loop.clean_output_folder') as mock_clean, \
             patch('tkinter.Tk') as mock_tk:
            
            # Mock Tk root window
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Run main function
            main()
            
            # Verify manual mode was selected (askyesno called twice: input mode + zip output)
            self.assertEqual(mock_askyesno.call_count, 2)
            # Verify manual parameter dialogs were called
            self.assertEqual(mock_askstring.call_count, 5)  # 5 string inputs (zip filename only if zip_output=True)
            self.assertEqual(mock_askinteger.call_count, 1)  # 1 integer input
            
            print("✓ Manual mode selection works correctly")
            print("✓ Manual parameter dialogs function properly")
    
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.messagebox.showerror')
    def test_csv_mode_no_file_selected(self, mock_showerror, mock_filedialog, mock_askyesno):
        """Test CSV mode when no file is selected"""
        
        # Mock user selecting CSV mode but canceling file dialog
        mock_askyesno.return_value = True
        mock_filedialog.return_value = ""  # Empty string = no file selected
        
        from generate_qr_codes_gui_loop import main
        
        with patch('tkinter.Tk') as mock_tk:
            # Mock Tk root window
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Run main function
            main()
            
            # Verify error message was shown
            mock_showerror.assert_called_once_with("Error", "No file selected. Exiting.")
            
            print("✓ Error handling works when no CSV file selected")

def run_automated_tests():
    """Run all automated tests"""
    print("Running automated CSV dialog tests:")
    print("-" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCSVDialog)
    
    # Run tests with custom result handler
    class CustomTestResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            
        def addError(self, test, err):
            super().addError(test, err)
            print(f"✗ ERROR in {test._testMethodName}: {err[1]}")
            
        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"✗ FAILURE in {test._testMethodName}: {err[1]}")
    
    runner = unittest.TextTestRunner(resultclass=CustomTestResult, verbosity=0)
    result = runner.run(suite)
    
    print("-" * 50)
    if result.wasSuccessful():
        print("✅ All automated tests passed!")
    else:
        print(f"❌ {len(result.failures + result.errors)} test(s) failed")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_automated_tests()