#!/usr/bin/env python3
"""Test input validation functionality"""

import sys
import os
import unittest

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestInputValidation(unittest.TestCase):
    
    def test_validate_integer_input_valid(self):
        """Test valid integer inputs"""
        from generate_qr_codes_gui_loop import validate_integer_input
        
        # Valid cases
        self.assertEqual(validate_integer_input("5", "Test", 1, 10), (True, 5))
        self.assertEqual(validate_integer_input("1", "Test", 1, 10), (True, 1))
        self.assertEqual(validate_integer_input("10", "Test", 1, 10), (True, 10))
        self.assertEqual(validate_integer_input("100", "Test", 1), (True, 100))  # No max limit
    
    def test_validate_integer_input_invalid(self):
        """Test invalid integer inputs"""
        from generate_qr_codes_gui_loop import validate_integer_input
        
        # Invalid cases
        valid, msg = validate_integer_input("0", "Test", 1, 10)
        self.assertFalse(valid)
        self.assertIn("must be at least 1", msg)
        
        valid, msg = validate_integer_input("11", "Test", 1, 10)
        self.assertFalse(valid)
        self.assertIn("must be at most 10", msg)
        
        valid, msg = validate_integer_input("abc", "Test", 1, 10)
        self.assertFalse(valid)
        self.assertIn("must be a valid number", msg)
        
        valid, msg = validate_integer_input("-5", "Test", 1, 10)
        self.assertFalse(valid)
        self.assertIn("must be at least 1", msg)
    
    def test_validate_date_format_valid(self):
        """Test valid date formats"""
        from generate_qr_codes_gui_loop import validate_date_format
        
        # Valid dates
        self.assertEqual(validate_date_format("26.12.31"), (True, "26.12.31"))
        self.assertEqual(validate_date_format("01.01.00"), (True, "01.01.00"))
        self.assertEqual(validate_date_format("31.12.99"), (True, "31.12.99"))
        self.assertEqual(validate_date_format("15.06.25"), (True, "15.06.25"))
    
    def test_validate_date_format_invalid(self):
        """Test invalid date formats"""
        from generate_qr_codes_gui_loop import validate_date_format
        
        # Invalid formats
        valid, msg = validate_date_format("")
        self.assertFalse(valid)
        self.assertIn("Date cannot be empty", msg)
        
        valid, msg = validate_date_format("2024-12-31")
        self.assertFalse(valid)
        self.assertIn("DD.MM.YY format", msg)
        
        valid, msg = validate_date_format("31.13.31")  # Month 13
        self.assertFalse(valid)
        self.assertIn("Invalid date", msg)
        
        valid, msg = validate_date_format("32.12.31")  # Day 32
        self.assertFalse(valid)
        self.assertIn("Invalid date", msg)
        
        valid, msg = validate_date_format("1.1.31")  # Single digits
        self.assertFalse(valid)
        self.assertIn("DD.MM.YY format", msg)
    
    def test_validate_color_format_valid(self):
        """Test valid color formats"""
        from generate_qr_codes_gui_loop import validate_color_format
        
        # Valid hex colors
        self.assertEqual(validate_color_format("#000000"), (True, "#000000"))
        self.assertEqual(validate_color_format("#FFF"), (True, "#FFF"))
        self.assertEqual(validate_color_format("#ff0000"), (True, "#ff0000"))
        self.assertEqual(validate_color_format("#123ABC"), (True, "#123ABC"))
        
        # Valid CSS color names
        self.assertEqual(validate_color_format("red"), (True, "red"))
        self.assertEqual(validate_color_format("BLACK"), (True, "BLACK"))
        self.assertEqual(validate_color_format("blue"), (True, "blue"))
        self.assertEqual(validate_color_format("orange"), (True, "orange"))
    
    def test_validate_color_format_invalid(self):
        """Test invalid color formats"""
        from generate_qr_codes_gui_loop import validate_color_format
        
        # Invalid cases
        valid, msg = validate_color_format("")
        self.assertFalse(valid)
        self.assertIn("Color cannot be empty", msg)
        
        valid, msg = validate_color_format("#GGG")  # Invalid hex
        self.assertFalse(valid)
        self.assertIn("Invalid hex color format", msg)
        
        valid, msg = validate_color_format("#12345")  # Wrong length
        self.assertFalse(valid)
        self.assertIn("#RGB or #RRGGBB format", msg)
        
        valid, msg = validate_color_format("invalidcolor")  # Unknown color name
        self.assertFalse(valid)
        self.assertIn("hex format", msg)
        
        valid, msg = validate_color_format("rgb(255,0,0)")  # RGB function not supported
        self.assertFalse(valid)
        self.assertIn("hex format", msg)
    
    def test_validate_format_valid(self):
        """Test valid format inputs"""
        from generate_qr_codes_gui_loop import validate_format
        
        # Valid formats
        self.assertEqual(validate_format("png"), (True, "png"))
        self.assertEqual(validate_format("svg"), (True, "svg"))
        self.assertEqual(validate_format("PNG"), (True, "png"))
        self.assertEqual(validate_format("SVG"), (True, "svg"))
    
    def test_validate_format_invalid(self):
        """Test invalid format inputs"""
        from generate_qr_codes_gui_loop import validate_format
        
        # Invalid cases
        valid, msg = validate_format("")
        self.assertFalse(valid)
        self.assertIn("Format cannot be empty", msg)
        
        valid, msg = validate_format("jpg")
        self.assertFalse(valid)
        self.assertIn("Format must be one of", msg)
        
        valid, msg = validate_format("gif")
        self.assertFalse(valid)
        self.assertIn("Format must be one of", msg)
    
    def test_validation_edge_cases(self):
        """Test edge cases and boundary conditions"""
        from generate_qr_codes_gui_loop import validate_integer_input, validate_date_format
        
        # Integer validation edge cases
        self.assertEqual(validate_integer_input("1", "Test", 1, 1), (True, 1))  # Min equals max
        
        valid, msg = validate_integer_input(None, "Test", 1, 10)
        self.assertFalse(valid)
        
        # Date validation edge cases
        self.assertEqual(validate_date_format("29.02.00"), (True, "29.02.00"))  # Leap year (2000)
        
        valid, msg = validate_date_format("29.02.01")  # Non-leap year (2001)
        self.assertFalse(valid)
        self.assertIn("Invalid date", msg)

if __name__ == '__main__':
    unittest.main()