#!/usr/bin/env python3
"""
Test script for format-specific options (Task 18)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generate_qr_codes_gui_loop import validate_png_quality, validate_svg_precision

def test_png_quality_validation():
    """Test PNG quality validation"""
    print("Testing PNG quality validation...")
    
    # Valid cases
    valid, result = validate_png_quality("85")
    assert valid == True and result == 85, f"Expected (True, 85), got ({valid}, {result})"
    
    valid, result = validate_png_quality("0")
    assert valid == True and result == 0, f"Expected (True, 0), got ({valid}, {result})"
    
    valid, result = validate_png_quality("100")
    assert valid == True and result == 100, f"Expected (True, 100), got ({valid}, {result})"
    
    # Invalid cases
    valid, result = validate_png_quality("-1")
    assert valid == False, f"Expected False for -1, got {valid}"
    
    valid, result = validate_png_quality("101")
    assert valid == False, f"Expected False for 101, got {valid}"
    
    valid, result = validate_png_quality("abc")
    assert valid == False, f"Expected False for 'abc', got {valid}"
    
    valid, result = validate_png_quality("")
    assert valid == False, f"Expected False for empty string, got {valid}"
    
    print("✅ PNG quality validation tests passed!")

def test_svg_precision_validation():
    """Test SVG precision validation"""
    print("Testing SVG precision validation...")
    
    # Valid cases
    valid, result = validate_svg_precision("2")
    assert valid == True and result == 2, f"Expected (True, 2), got ({valid}, {result})"
    
    valid, result = validate_svg_precision("0")
    assert valid == True and result == 0, f"Expected (True, 0), got ({valid}, {result})"
    
    valid, result = validate_svg_precision("10")
    assert valid == True and result == 10, f"Expected (True, 10), got ({valid}, {result})"
    
    # Invalid cases
    valid, result = validate_svg_precision("-1")
    assert valid == False, f"Expected False for -1, got {valid}"
    
    valid, result = validate_svg_precision("11")
    assert valid == False, f"Expected False for 11, got {valid}"
    
    valid, result = validate_svg_precision("abc")
    assert valid == False, f"Expected False for 'abc', got {valid}"
    
    valid, result = validate_svg_precision("")
    assert valid == False, f"Expected False for empty string, got {valid}"
    
    print("✅ SVG precision validation tests passed!")

def test_format_specific_parameters():
    """Test that format-specific parameters can be passed to create_qr_codes"""
    print("Testing format-specific parameters...")
    
    from generate_qr_codes_gui_loop import create_qr_codes
    import tempfile
    import os
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test PNG with quality parameter
        try:
            create_qr_codes(
                valid_uses="1", volume="100", end_date="31.12.25", 
                color="#000000", output_folder=temp_dir, format="png", 
                count=1, png_quality=95, svg_precision=2
            )
            
            # Check if file was created
            files = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
            assert len(files) == 1, f"Expected 1 PNG file, found {len(files)}"
            print("✅ PNG generation with quality parameter successful!")
        except Exception as e:
            print(f"❌ PNG generation failed: {e}")
            raise
        
        # Test SVG with precision parameter
        try:
            create_qr_codes(
                valid_uses="1", volume="100", end_date="31.12.25", 
                color="#000000", output_folder=temp_dir, format="svg", 
                count=1, png_quality=85, svg_precision=3
            )
            
            # Check if file was created
            files = [f for f in os.listdir(temp_dir) if f.endswith('.svg')]
            assert len(files) == 1, f"Expected 1 SVG file, found {len(files)}"
            print("✅ SVG generation with precision parameter successful!")
        except Exception as e:
            print(f"❌ SVG generation failed: {e}")
            raise

if __name__ == "__main__":
    print("Testing format-specific options implementation (Task 18)...")
    print("=" * 60)
    
    test_png_quality_validation()
    test_svg_precision_validation()
    test_format_specific_parameters()
    
    print("=" * 60)
    print("🎉 All tests passed! Task 18 implementation is working correctly.")