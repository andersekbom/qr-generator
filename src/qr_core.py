"""
Core QR code generation functionality for QR Generator Pro
Contains the main QR code creation and file processing logic
"""

import os
import qrcode
import qrcode.image.svg
import xml.etree.ElementTree as ET
import re
from tqdm import tqdm
from src.validation import get_error_correction_level


def generate_custom_filename(base_name, prefix="", suffix="", use_payload_as_base=True, index=None):
    """Generate custom filename with optional prefix/suffix"""
    if use_payload_as_base:
        # Create safe filename from payload/base_name
        safe_base = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip('.')
        if not safe_base:
            safe_base = f"qr_code_{index}" if index is not None else "qr_code"
    else:
        # Use index-based naming
        safe_base = f"qr_code_{index}" if index is not None else "qr_code"
    
    # Combine prefix, base, and suffix
    filename_parts = []
    if prefix:
        filename_parts.append(prefix)
    filename_parts.append(safe_base)
    if suffix:
        filename_parts.append(suffix)
    
    return "_".join(filename_parts)


def create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count, csv_data=None, input_column=0, security_code="SECD", suffix_code="23FF45EE", qr_version=None, error_correction="L", box_size=10, border=4, filename_prefix="", filename_suffix="", use_payload_as_filename=True, png_quality=85, svg_precision=2, progress_callback=None):
    """
    Create QR codes either from manual parameters or CSV data
    
    Args:
        csv_data: List of CSV rows (None for manual mode)
        input_column: Column index to use from CSV data
        security_code: Security code to include in payload (default: "SECD")
        suffix_code: Suffix code to include in payload (default: "23FF45EE")
        qr_version: QR code version (1-40, None for auto)
        error_correction: Error correction level (L, M, Q, H)
        box_size: Size of each QR code box in pixels
        border: Border size in boxes
        filename_prefix: Prefix to add to generated filenames
        filename_suffix: Suffix to add to generated filenames (before extension)
        use_payload_as_filename: Whether to use payload content as filename base
        png_quality: Quality setting for PNG images (0-100, higher is better quality)
        svg_precision: Decimal precision for SVG coordinates
        progress_callback: Optional callback function for progress updates
        Other parameters: Used for manual mode or as defaults
    """
    os.makedirs(output_folder, exist_ok=True)
    factory = qrcode.image.svg.SvgFillImage if format == 'svg' else None
    
    # Get error correction level
    error_correction_level = get_error_correction_level(error_correction)

    if csv_data is not None:
        # CSV mode: generate QR codes from CSV data
        total_rows = len(csv_data)
        for i, row in enumerate(csv_data):
            if progress_callback:
                progress_callback(i, total_rows, f"Processing CSV row {i+1}/{total_rows}")
            
            if len(row) <= input_column:
                print(f"Warning: Row {i+1} doesn't have column {input_column}, skipping")
                continue
            
            payload = row[input_column]
            qr = qrcode.QRCode(
                version=qr_version,
                error_correction=error_correction_level,
                box_size=box_size,
                border=border,
            )
            qr.add_data(payload, optimize=0)
            qr.make(fit=True)

            img = qr.make_image(fill_color=color, back_color="#FFFFFF", image_factory=factory)

            # Generate custom filename
            custom_filename = generate_custom_filename(
                payload, filename_prefix, filename_suffix, 
                use_payload_as_filename, i+1
            )
            filename = os.path.join(output_folder, f"{custom_filename}.{format}")
            
            if format == 'png':
                # Apply PNG quality settings
                img.save(filename, "PNG", optimize=True, quality=png_quality)
            elif format == 'svg':
                img.save(filename)
                colorize_svg(filename, color, svg_precision=svg_precision)
            else:
                img.save(filename)
    else:
        # Manual mode: generate QR codes with sequential serials
        for i in range(1, count + 1):
            if progress_callback:
                progress_callback(i-1, count, f"Generating QR code {i}/{count}")
            
            serial = f"{i:08d}"
            payload = f"M-{valid_uses}-{serial}-{volume}-{end_date}-{security_code}-{suffix_code}"
            qr = qrcode.QRCode(
                version=qr_version,
                error_correction=error_correction_level,
                box_size=box_size,
                border=border,
            )
            qr.add_data(payload, optimize=0)
            qr.make(fit=True)

            img = qr.make_image(fill_color=color, back_color="#FFFFFF", image_factory=factory)

            # Generate custom filename
            custom_filename = generate_custom_filename(
                payload, filename_prefix, filename_suffix, 
                use_payload_as_filename, i
            )
            filename = os.path.join(output_folder, f"{custom_filename}.{format}")
            
            if format == 'png':
                # Apply PNG quality settings
                img.save(filename, "PNG", optimize=True, quality=png_quality)
            elif format == 'svg':
                img.save(filename)
                colorize_svg(filename, color, svg_precision=svg_precision)
            else:
                img.save(filename)
    
    # Final progress callback to indicate completion
    if progress_callback:
        if csv_data is not None:
            progress_callback(len(csv_data), len(csv_data), "CSV processing complete!")
        else:
            progress_callback(count, count, "QR code generation complete!")
    
    # Return the output folder path for results display
    return output_folder


def colorize_svg(svg_file, color, background_color="#FFFFFF", svg_precision=2):
    """
    Colorize SVG using proper XML manipulation with namespace handling.
    
    Args:
        svg_file (str): Path to SVG file
        color (str): Foreground color for QR code modules
        background_color (str): Background color (default white)
        svg_precision (int): Decimal precision for SVG coordinates
    """
    try:
        # Read the SVG file
        with open(svg_file, 'r') as file:
            svg_content = file.read()
        
        # Parse the SVG string with XML
        try:
            root = ET.fromstring(svg_content)
        except ET.ParseError as e:
            print(f"Warning: Could not parse SVG as XML ({e}), falling back to regex method")
            # Fallback to original regex method if XML parsing fails
            colored_svg = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg_content)
            with open(svg_file, 'w') as file:
                file.write(colored_svg)
            return
        
        # Register SVG namespace to handle namespace prefixes properly
        ET.register_namespace('svg', 'http://www.w3.org/2000/svg')
        namespace = "{http://www.w3.org/2000/svg}"
        
        # Track if we modified anything
        modified = False
        
        # Find and color path elements (for path-based QR codes)
        path_elements = root.findall(f".//{namespace}path")
        if not path_elements:
            path_elements = root.findall(".//path")  # Try without namespace
        
        for path_element in path_elements:
            path_element.set("fill", color)
            modified = True
        
        # Find and color rect elements (for rect-based QR codes like SvgFillImage)
        rect_elements = root.findall(f".//{namespace}rect")
        if not rect_elements:
            rect_elements = root.findall(".//rect")  # Try without namespace
        
        # The first rect is usually the background, others are QR modules
        for i, rect_element in enumerate(rect_elements):
            if i == 0:
                # First rect is typically the background
                rect_element.set("fill", background_color)
            else:
                # Other rects are QR code modules
                rect_element.set("fill", color)
            modified = True
        
        if not modified:
            print("Warning: Could not find path or rect elements in SVG. Falling back to regex method.")
            # Fallback to regex if no elements found
            colored_svg = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg_content)
            with open(svg_file, 'w') as file:
                file.write(colored_svg)
            return
        
        # Write the modified SVG back to file
        modified_svg_string = ET.tostring(root, encoding='unicode')
        
        # Apply precision formatting to numeric values in SVG
        if svg_precision < 10:  # Only apply precision formatting if it's reasonable
            # Format decimal numbers to specified precision
            def format_number(match):
                number = float(match.group())
                return f"{number:.{svg_precision}f}"
            
            # Match decimal numbers (including integers that could be formatted)
            modified_svg_string = re.sub(r'\b\d+\.\d+\b', format_number, modified_svg_string)
        
        # Ensure proper SVG declaration if missing
        if not modified_svg_string.startswith('<?xml'):
            modified_svg_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + modified_svg_string
        
        with open(svg_file, 'w') as file:
            file.write(modified_svg_string)
            
    except Exception as e:
        print(f"Warning: Error in XML-based SVG colorization ({e}), falling back to regex method")
        # Fallback to original regex method if anything goes wrong
        try:
            with open(svg_file, 'r') as file:
                svg_content = file.read()
            colored_svg = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg_content)
            with open(svg_file, 'w') as file:
                file.write(colored_svg)
        except Exception as fallback_error:
            print(f"Error: Both XML and regex colorization methods failed: {fallback_error}")