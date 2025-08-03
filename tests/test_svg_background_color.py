#!/usr/bin/env python3
"""Test background color support for SVG"""

import sys
import os
import unittest
import tempfile
import xml.etree.ElementTree as ET

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSVGBackgroundColor(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_background_color_application(self):
        """Test that background colors are properly applied to SVG"""
        from generate_qr_codes_gui_loop import colorize_svg
        
        # Create SVG with background rect
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect x="0" y="0" width="100" height="100" fill="#ffffff"/>
    <rect x="10" y="10" width="10" height="10" fill="#000000"/>
    <rect x="20" y="20" width="10" height="10" fill="#000000"/>
</svg>'''
        
        svg_path = os.path.join(self.test_dir, "test_background.svg")
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Apply colorization with custom background
        colorize_svg(svg_path, "#FF0000", "#00FF00")
        
        # Read and parse the result
        with open(svg_path, 'r') as f:
            result_content = f.read()
        
        root = ET.fromstring(result_content)
        namespace = "{http://www.w3.org/2000/svg}"
        
        # Find all rect elements
        rects = root.findall(f".//{namespace}rect")
        self.assertGreater(len(rects), 0)
        
        # First rect should be background (green)
        self.assertEqual(rects[0].get("fill"), "#00FF00")
        
        # Other rects should be foreground (red)
        for rect in rects[1:]:
            self.assertEqual(rect.get("fill"), "#FF0000")
    
    def test_both_colors_in_real_qr_code(self):
        """Test both foreground and background colors in real QR code generation"""
        import qrcode
        import qrcode.image.svg
        from generate_qr_codes_gui_loop import colorize_svg
        
        # Generate real QR code
        qr = qrcode.QRCode(version=1)
        qr.add_data("Test QR Code")
        qr.make(fit=True)
        
        img = qr.make_image(image_factory=qrcode.image.svg.SvgFillImage)
        svg_path = os.path.join(self.test_dir, "test_real_qr.svg")
        img.save(svg_path)
        
        # Apply both colors
        colorize_svg(svg_path, "#800080", "#FFFF00")  # Purple on yellow
        
        # Verify both colors are present
        with open(svg_path, 'r') as f:
            result_content = f.read()
        
        # Both colors should be in the SVG
        self.assertIn("#800080", result_content)  # Purple foreground
        self.assertIn("#FFFF00", result_content)  # Yellow background
        
        # Verify XML structure is maintained
        root = ET.fromstring(result_content)
        self.assertIsNotNone(root)

if __name__ == '__main__':
    unittest.main()