"""
Validation functions for QR Generator Pro
Extracted from main qr_generator.py file for better modularity
"""

import re
import qrcode.constants
from datetime import datetime


def validate_integer_input(value, field_name, min_value=1, max_value=None):
    """Validate integer input with range checking"""
    try:
        int_value = int(value)
        if int_value < min_value:
            return False, f"{field_name} must be at least {min_value}"
        if max_value is not None and int_value > max_value:
            return False, f"{field_name} must be at most {max_value}"
        return True, int_value
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"


def validate_date_format(date_str):
    """Validate date format (DD.MM.YY)"""
    if not date_str:
        return False, "Date cannot be empty"
    
    # Check basic format
    if not re.match(r'^\d{2}\.\d{2}\.\d{2}$', date_str):
        return False, "Date must be in DD.MM.YY format (e.g., 26.12.31)"
    
    try:
        # Parse and validate the date
        day, month, year = map(int, date_str.split('.'))
        
        # Add 2000 to year for proper datetime validation
        full_year = 2000 + year
        datetime(full_year, month, day)
        
        return True, date_str
    except ValueError:
        return False, "Invalid date. Please check day, month values."


def validate_color_format(color_str):
    """Validate color format (hex or CSS color name)"""
    if not color_str:
        return False, "Color cannot be empty"
    
    # Check hex format
    if color_str.startswith('#'):
        if len(color_str) not in [4, 7]:  # #RGB or #RRGGBB
            return False, "Hex color must be #RGB or #RRGGBB format"
        try:
            int(color_str[1:], 16)
            return True, color_str
        except ValueError:
            return False, "Invalid hex color format"
    
    # Allow common CSS color names
    css_colors = {
        'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
        'silver', 'gray', 'maroon', 'olive', 'lime', 'aqua', 'teal', 'navy',
        'fuchsia', 'purple', 'orange', 'brown', 'pink', 'gold'
    }
    
    if color_str.lower() in css_colors:
        return True, color_str
    
    return False, "Color must be hex format (#RGB or #RRGGBB) or CSS color name"


def validate_format(format_str):
    """Validate output format"""
    if not format_str:
        return False, "Format cannot be empty"
    
    valid_formats = ['png', 'svg']
    if format_str.lower() not in valid_formats:
        return False, f"Format must be one of: {', '.join(valid_formats)}"
    
    return True, format_str.lower()


def validate_qr_version(version_str):
    """Validate QR code version"""
    if not version_str or version_str.lower() == 'auto':
        return True, None
    
    try:
        version = int(version_str)
        if 1 <= version <= 40:
            return True, version
        else:
            return False, "QR version must be between 1 and 40, or 'auto'"
    except ValueError:
        return False, "QR version must be a number between 1-40 or 'auto'"


def validate_error_correction(level_str):
    """Validate error correction level"""
    if not level_str:
        return False, "Error correction level cannot be empty"
    
    valid_levels = ['L', 'M', 'Q', 'H']
    if level_str.upper() not in valid_levels:
        return False, f"Error correction must be one of: {', '.join(valid_levels)}"
    
    return True, level_str.upper()


def validate_png_quality(quality_str):
    """Validate PNG quality setting"""
    if not quality_str:
        return False, "PNG quality cannot be empty"
    
    try:
        quality = int(quality_str)
        if quality < 0 or quality > 100:
            return False, "PNG quality must be between 0 and 100"
        return True, quality
    except ValueError:
        return False, "PNG quality must be a valid number"


def validate_svg_precision(precision_str):
    """Validate SVG precision setting"""
    if not precision_str:
        return False, "SVG precision cannot be empty"
    
    try:
        precision = int(precision_str)
        if precision < 0 or precision > 10:
            return False, "SVG precision must be between 0 and 10"
        return True, precision
    except ValueError:
        return False, "SVG precision must be a valid number"


def get_error_correction_level(level_str):
    """Convert error correction string to qrcode constant"""
    levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    return levels.get(level_str.upper(), qrcode.constants.ERROR_CORRECT_L)