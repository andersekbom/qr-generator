"""
Preset management functionality for QR Generator Pro
Handles saving, loading, and managing parameter presets
"""

import os
import json
from tkinter import simpledialog


def get_presets_dir():
    """Get or create the presets directory"""
    presets_dir = os.path.join(os.getcwd(), "presets")
    os.makedirs(presets_dir, exist_ok=True)
    return presets_dir


def save_preset(preset_name, parameters):
    """Save parameter preset to JSON file"""
    try:
        presets_dir = get_presets_dir()
        preset_file = os.path.join(presets_dir, f"{preset_name}.json")
        
        with open(preset_file, 'w') as f:
            json.dump(parameters, f, indent=2)
        
        return True, f"Preset '{preset_name}' saved successfully"
    except Exception as e:
        return False, f"Failed to save preset: {e}"


def load_preset(preset_name):
    """Load parameter preset from JSON file"""
    try:
        presets_dir = get_presets_dir()
        preset_file = os.path.join(presets_dir, f"{preset_name}.json")
        
        if not os.path.exists(preset_file):
            return False, f"Preset '{preset_name}' not found"
        
        with open(preset_file, 'r') as f:
            parameters = json.load(f)
        
        return True, parameters
    except Exception as e:
        return False, f"Failed to load preset: {e}"


def list_presets():
    """List all available presets"""
    try:
        presets_dir = get_presets_dir()
        preset_files = [f for f in os.listdir(presets_dir) if f.endswith('.json')]
        preset_names = [os.path.splitext(f)[0] for f in preset_files]
        return preset_names
    except Exception:
        return []


def delete_preset(preset_name):
    """Delete a parameter preset"""
    try:
        presets_dir = get_presets_dir()
        preset_file = os.path.join(presets_dir, f"{preset_name}.json")
        
        if not os.path.exists(preset_file):
            return False, f"Preset '{preset_name}' not found"
        
        os.remove(preset_file)
        return True, f"Preset '{preset_name}' deleted successfully"
    except Exception as e:
        return False, f"Failed to delete preset: {e}"


def create_manual_mode_preset(valid_uses, volume, end_date, color, format, security_code, suffix_code, qr_version=None, error_correction="L", box_size=10, border=4, filename_prefix="", filename_suffix="", use_payload_as_filename=True, png_quality=85, svg_precision=2):
    """Create preset dictionary for manual mode parameters"""
    return {
        "mode": "manual",
        "valid_uses": valid_uses,
        "volume": volume,
        "end_date": end_date,
        "color": color,
        "format": format,
        "security_code": security_code,
        "suffix_code": suffix_code,
        "qr_version": qr_version,
        "error_correction": error_correction,
        "box_size": box_size,
        "border": border,
        "filename_prefix": filename_prefix,
        "filename_suffix": filename_suffix,
        "use_payload_as_filename": use_payload_as_filename,
        "png_quality": png_quality,
        "svg_precision": svg_precision
    }


def create_csv_mode_preset(format, color, qr_version=None, error_correction="L", box_size=10, border=4, filename_prefix="", filename_suffix="", use_payload_as_filename=True, delimiter=",", input_column=0, skip_first_row=False, png_quality=85, svg_precision=2):
    """Create preset dictionary for CSV mode parameters"""
    return {
        "mode": "csv",
        "format": format,
        "color": color,
        "qr_version": qr_version,
        "error_correction": error_correction,
        "box_size": box_size,
        "border": border,
        "filename_prefix": filename_prefix,
        "filename_suffix": filename_suffix,
        "use_payload_as_filename": use_payload_as_filename,
        "delimiter": delimiter,
        "input_column": input_column,
        "skip_first_row": skip_first_row,
        "png_quality": png_quality,
        "svg_precision": svg_precision
    }


def show_preset_menu():
    """Show preset management menu and return user choice"""
    available_presets = list_presets()
    preset_list = "\n".join([f"- {name}" for name in available_presets]) if available_presets else "No presets available"
    
    menu_text = f"""Preset Management:

Available presets:
{preset_list}

Choose action:
1. Load preset
2. Save current parameters as preset
3. Delete preset
4. Continue without presets"""
    
    choice = simpledialog.askstring("Preset Management", menu_text + "\n\nEnter choice (1-4):")
    return choice, available_presets