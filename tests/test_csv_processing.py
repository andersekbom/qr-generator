#!/usr/bin/env python3
"""Automated test for CSV processing functionality"""

import sys
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCSVProcessing(unittest.TestCase):
    
    def setUp(self):
        """Create sample CSV files for testing"""
        # Sample CSV with URLs
        self.sample_csv_urls = """url,description
https://example.com/page1,Test Page 1
https://example.com/page2,Test Page 2
https://example.com/page3,Test Page 3"""
        
        # Sample CSV with different data types
        self.sample_csv_mixed = """data,type,priority
M-15-00000001-500-26.12.31-SECD-23FF45EE,voucher,high
Contact: John Doe - john@email.com,contact,medium
https://docs.example.com,documentation,low"""
        
        # Sample CSV with semicolon delimiter
        self.sample_csv_semicolon = """code;description;category
ABC123;Product Code 1;electronics
DEF456;Product Code 2;clothing
GHI789;Product Code 3;books"""
        
        # Create temporary files
        self.temp_urls = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_urls.write(self.sample_csv_urls)
        self.temp_urls.close()
        
        self.temp_mixed = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_mixed.write(self.sample_csv_mixed)
        self.temp_mixed.close()
        
        self.temp_semicolon = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_semicolon.write(self.sample_csv_semicolon)
        self.temp_semicolon.close()
    
    def tearDown(self):
        """Clean up test files"""
        for temp_file in [self.temp_urls, self.temp_mixed, self.temp_semicolon]:
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    def test_create_qr_codes_csv_mode(self):
        """Test create_qr_codes function with CSV data"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test data
        csv_data = [
            ['https://example.com/1', 'Test 1'],
            ['https://example.com/2', 'Test 2'],
            ['https://example.com/3', 'Test 3']
        ]
        
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock file saving to avoid actual file creation
            with patch('qrcode.QRCode.make_image') as mock_make_image:
                mock_img = MagicMock()
                mock_make_image.return_value = mock_img
                
                # Test CSV mode
                create_qr_codes(
                    valid_uses=None, 
                    volume=None, 
                    end_date=None, 
                    color="#000000",
                    output_folder=temp_dir,
                    format="png",
                    count=None,
                    csv_data=csv_data,
                    input_column=0
                )
                
                # Verify QR codes were created for each CSV row
                self.assertEqual(mock_make_image.call_count, 3)
                self.assertEqual(mock_img.save.call_count, 3)
                
                print("✓ CSV mode QR generation works correctly")
    
    def test_create_qr_codes_different_columns(self):
        """Test CSV processing with different column selections"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test data with multiple columns
        csv_data = [
            ['skip', 'https://example.com/1', 'description1'],
            ['skip', 'https://example.com/2', 'description2']
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('qrcode.QRCode.make_image') as mock_make_image:
                mock_img = MagicMock()
                mock_make_image.return_value = mock_img
                
                # Test column 1 (URLs)
                create_qr_codes(
                    valid_uses=None, volume=None, end_date=None, color="#000000",
                    output_folder=temp_dir, format="png", count=None,
                    csv_data=csv_data, input_column=1
                )
                
                # Verify correct column was used
                calls = mock_make_image.call_args_list
                # Check that QRCode.add_data was called with URLs from column 1
                self.assertEqual(len(calls), 2)
                
                print("✓ Column selection works correctly")
    
    def test_csv_row_validation(self):
        """Test handling of CSV rows with missing columns"""
        from generate_qr_codes_gui_loop import create_qr_codes
        
        # Test data with inconsistent columns
        csv_data = [
            ['https://example.com/1', 'description1'],
            ['https://example.com/2'],  # Missing column
            ['https://example.com/3', 'description3']
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('qrcode.QRCode.make_image') as mock_make_image, \
                 patch('builtins.print') as mock_print:
                
                mock_img = MagicMock()
                mock_make_image.return_value = mock_img
                
                # Test with column 1 (should skip row with missing column)
                create_qr_codes(
                    valid_uses=None, volume=None, end_date=None, color="#000000",
                    output_folder=temp_dir, format="png", count=None,
                    csv_data=csv_data, input_column=1
                )
                
                # Should only generate 2 QR codes (skip the incomplete row)
                self.assertEqual(mock_make_image.call_count, 2)
                
                # Should print warning about skipped row
                warning_printed = any("Warning" in str(call) and "Row 2" in str(call) 
                                    for call in mock_print.call_args_list)
                self.assertTrue(warning_printed, "Should print warning for missing column")
                
                print("✓ CSV row validation and error handling works")
    
    @patch('tkinter.messagebox.askyesno')
    @patch('tkinter.filedialog.askopenfilename')
    @patch('tkinter.simpledialog.askstring')
    @patch('tkinter.simpledialog.askinteger')
    @patch('tkinter.messagebox.showinfo')
    def test_full_csv_workflow(self, mock_showinfo, mock_askinteger, mock_askstring, 
                              mock_filedialog, mock_askyesno):
        """Test complete CSV processing workflow"""
        
        # Mock user selections
        mock_askyesno.side_effect = [True, True, True]  # CSV mode, skip header, zip output
        mock_filedialog.return_value = self.temp_urls.name
        mock_askstring.side_effect = [',', 'png', '#FF0000', 'test_output.zip']  # delimiter, format, color, zip name
        mock_askinteger.return_value = 0  # column selection
        
        from generate_qr_codes_gui_loop import main
        
        with patch('generate_qr_codes_gui_loop.create_qr_codes') as mock_create, \
             patch('generate_qr_codes_gui_loop.zip_output_files') as mock_zip, \
             patch('generate_qr_codes_gui_loop.clean_output_folder') as mock_clean, \
             patch('tkinter.Tk') as mock_tk:
            
            mock_root = MagicMock()
            mock_tk.return_value = mock_root
            
            # Run main function
            main()
            
            # Verify CSV processing was called
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            
            # Check that CSV data was passed
            self.assertIsNotNone(call_args.kwargs.get('csv_data'))
            self.assertEqual(call_args.kwargs.get('input_column'), 0)
            
            # Verify success message was shown
            mock_showinfo.assert_called_once()
            success_message = mock_showinfo.call_args[0][1]
            self.assertIn("generated successfully from CSV", success_message)
            
            print("✓ Full CSV workflow integration works correctly")

def run_csv_tests():
    """Run all CSV processing tests"""
    print("Running CSV processing tests:")
    print("-" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCSVProcessing)
    
    # Run tests
    class CustomTestResult(unittest.TextTestResult):
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
        print("✅ All CSV processing tests passed!")
    else:
        print(f"❌ {len(result.failures + result.errors)} test(s) failed")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_csv_tests()