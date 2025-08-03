#!/usr/bin/env python3
"""Test XML namespace handling for SVG colorization"""

import sys
import os
import unittest
import tempfile
import xml.etree.ElementTree as ET

# Add parent directory to path to import the main module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSVGColorization(unittest.TestCase):
    
    def setUp(self):
        """Create temporary directory for test files"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_xml_namespace_svg_colorization(self):
        """Test proper XML namespace handling for SVG colorization"""
        from generate_qr_codes_gui_loop import colorize_svg
        
        # Create a sample SVG with proper namespace
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
    <rect x="0" y="0" width="100" height="100" fill="#ffffff"/>
    <path d="M10,10 L90,10 L90,90 L10,90 Z" fill="#000000"/>
</svg>'''
        
        svg_path = os.path.join(self.test_dir, "test_namespaced.svg")
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Apply colorization
        colorize_svg(svg_path, "#FF0000", "#00FF00")
        
        # Read and parse the result
        with open(svg_path, 'r') as f:
            result_content = f.read()
        
        # Parse XML to verify changes
        root = ET.fromstring(result_content)
        namespace = "{http://www.w3.org/2000/svg}"
        
        # Check path color (foreground)
        path_element = root.find(f".//{namespace}path")
        self.assertIsNotNone(path_element)
        self.assertEqual(path_element.get("fill"), "#FF0000")
        
        # Check rect color (background)
        rect_element = root.find(f".//{namespace}rect")
        self.assertIsNotNone(rect_element)
        self.assertEqual(rect_element.get("fill"), "#00FF00")
    
    def test_svg_without_namespace(self):
        """Test SVG colorization without namespace declaration"""
        from generate_qr_codes_gui_loop import colorize_svg
        
        # Create SVG without namespace
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100">
    <rect x="0" y="0" width="100" height="100" fill="#ffffff"/>
    <path d="M10,10 L90,10 L90,90 L10,90 Z" fill="#000000"/>
</svg>'''
        
        svg_path = os.path.join(self.test_dir, "test_no_namespace.svg")
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Apply colorization
        colorize_svg(svg_path, "#0000FF", "#FFFF00")
        
        # Read and parse the result
        with open(svg_path, 'r') as f:
            result_content = f.read()
        
        # Parse XML to verify changes
        root = ET.fromstring(result_content)
        
        # Check path color (foreground) - should work without namespace
        path_element = root.find(".//path")
        self.assertIsNotNone(path_element)
        self.assertEqual(path_element.get("fill"), "#0000FF")
        
        # Check rect color (background)
        rect_element = root.find(".//rect")
        self.assertIsNotNone(rect_element)
        self.assertEqual(rect_element.get("fill"), "#FFFF00")
    
    def test_malformed_svg_fallback(self):
        """Test fallback to regex method for malformed SVG"""
        from generate_qr_codes_gui_loop import colorize_svg
        
        # Create malformed SVG that can't be parsed as XML
        svg_content = '''<svg width="100" height="100">
    <rect x="0" y="0" width="100" height="100" fill="#ffffff"/>
    <path d="M10,10 L90,10 L90,90 L10,90 Z" fill="#000000"/>
    <unclosed_tag>
</svg>'''
        
        svg_path = os.path.join(self.test_dir, "test_malformed.svg")
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Apply colorization - should fallback to regex
        # Note: We can't test logging easily since colorize_svg uses print()
        colorize_svg(svg_path, "#FF00FF")
        
        # Check that file was still modified (regex fallback worked)
        with open(svg_path, 'r') as f:
            result_content = f.read()
        
        # Should contain the new color from regex replacement
        self.assertIn('#FF00FF', result_content)
    
    def test_svg_generation_and_colorization(self):
        """Test complete SVG generation and colorization workflow"""
        import qrcode
        import qrcode.image.svg
        from generate_qr_codes_gui_loop import colorize_svg
        
        # Generate a real SVG QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data("https://www.example.com")
        qr.make(fit=True)
        
        # Create SVG image
        img = qr.make_image(image_factory=qrcode.image.svg.SvgFillImage)
        svg_path = os.path.join(self.test_dir, "test_generated.svg")
        img.save(svg_path)
        
        # Apply colorization
        colorize_svg(svg_path, "#800080", "#F0F0F0")
        
        # Verify the SVG was modified
        with open(svg_path, 'r') as f:
            result_content = f.read()
        
        # Should contain our custom colors (in XML format without # sometimes)
        self.assertTrue('#800080' in result_content or '#800080' in result_content.replace('fill="', '').replace('"', ''))
        self.assertTrue('#F0F0F0' in result_content or '#F0F0F0' in result_content.replace('fill="', '').replace('"', ''))
        
        # Verify it's still valid XML
        try:
            root = ET.fromstring(result_content)
            self.assertIsNotNone(root)
            
            # Verify we have the expected structure
            namespace = "{http://www.w3.org/2000/svg}"
            rects = root.findall(f".//{namespace}rect")
            if not rects:
                rects = root.findall(".//rect")
            
            # Should have at least one rect element (background + QR modules)
            self.assertGreater(len(rects), 0)
            
        except ET.ParseError:
            self.fail("Colorized SVG is not valid XML")

if __name__ == '__main__':
    unittest.main()