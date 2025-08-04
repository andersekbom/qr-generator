import qrcode
import qrcode.image.svg
import csv
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
import re
from tqdm import tqdm
import xml.etree.ElementTree as ET
from datetime import datetime
import json

import PIL
from PIL import Image, ImageDraw


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

def detect_delimiter(file_path):
    with open(file_path, "r") as infile:
        sample = infile.read(1024)
        return csv.Sniffer().sniff(sample).delimiter

def create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count, csv_data=None, input_column=0, security_code="SECD", suffix_code="23FF45EE", qr_version=None, error_correction="L", box_size=10, border=4, filename_prefix="", filename_suffix="", use_payload_as_filename=True, png_quality=85, svg_precision=2):
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
        Other parameters: Used for manual mode or as defaults
    """
    os.makedirs(output_folder, exist_ok=True)
    factory = qrcode.image.svg.SvgFillImage if format == 'svg' else None
    
    # Get error correction level
    error_correction_level = get_error_correction_level(error_correction)

    if csv_data is not None:
        # CSV mode: generate QR codes from CSV data
        for i, row in enumerate(tqdm(csv_data, desc="Generating QR codes from CSV")):
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
        for i in tqdm(range(1, count + 1), desc="Generating QR codes"):
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

            img = qr.make_image(fill_color=color, back_color="#000000", image_factory=factory)

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

def zip_output_files(output_folder, zip_file_name, format):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith(f".{format}"):
                    zipf.write(os.path.join(root, file), arcname=file)
    #messagebox.showinfo("Success", f"Output files added to zip file '{zip_file_name}' successfully!")

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

def clean_output_folder(output_folder):
    for root, _, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))


class QRGeneratorGUI:
    """Modern GUI interface for QR Generator using CustomTkinter"""
    
    def __init__(self):
        # Set CustomTkinter appearance mode and color theme
        ctk.set_appearance_mode("system")  # Modes: "system", "dark", "light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("QR Generator v2.0")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Center window on screen
        self.center_window()
        
        # Initialize GUI state variables
        self.operation_mode = tk.StringVar(value="single")  # single, batch, csv
        self.selected_preset = tk.StringVar(value="")
        self.csv_file_path = tk.StringVar(value="")
        
        # Create main layout
        self.create_main_layout()
        
        # Initialize with default values
        self.init_default_values()
    
    def center_window(self):
        """Center the main window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_main_layout(self):
        """Create the main window layout with sections"""
        # Configure grid weights for responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Header section
        self.create_header_section()
        
        # Main content area (scrollable)
        self.create_content_area()
        
        # Footer with action buttons
        self.create_footer_section()
    
    def create_header_section(self):
        """Create header with title and theme toggle"""
        header_frame = ctk.CTkFrame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="QR Code Generator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Theme toggle button
        theme_button = ctk.CTkButton(
            header_frame,
            text="🌙/☀️",
            width=50,
            command=self.toggle_theme
        )
        theme_button.grid(row=0, column=2, padx=20, pady=15, sticky="e")
    
    def create_content_area(self):
        """Create scrollable content area for all settings"""
        # Create scrollable frame
        self.content_frame = ctk.CTkScrollableFrame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder sections (will be implemented in subsequent tasks)
        self.create_placeholder_sections()
    
    def create_placeholder_sections(self):
        """Create placeholder sections for development"""
        # Operation Mode Section (Task 22) - IMPLEMENTED
        self.create_operation_mode_section()
        
        # Additional placeholder sections for other tasks
        
        # Preset Management Section (Task 23)
        preset_frame = ctk.CTkFrame(self.content_frame)
        preset_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        preset_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(preset_frame, text="Presets:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=20, pady=15, sticky="w")
        ctk.CTkLabel(preset_frame, text="[Coming in Task 23]", text_color="gray").grid(
            row=0, column=1, padx=20, pady=15, sticky="w")
        
        # Parameters Section (Task 25)
        params_frame = ctk.CTkFrame(self.content_frame)
        params_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        params_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(params_frame, text="Parameters:", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=20, pady=15, sticky="w")
        ctk.CTkLabel(params_frame, text="[Coming in Task 25]", text_color="gray").grid(
            row=0, column=1, padx=20, pady=15, sticky="w")
    
    def create_footer_section(self):
        """Create footer with main action buttons"""
        footer_frame = ctk.CTkFrame(self.root)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Generate button
        self.generate_button = ctk.CTkButton(
            footer_frame,
            text="Generate QR Codes",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            command=self.generate_qr_codes
        )
        self.generate_button.grid(row=0, column=2, padx=20, pady=15, sticky="e")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="Ready to generate QR codes",
            text_color="gray"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
    
    def create_operation_mode_section(self):
        """Create operation mode selection with clear radio buttons (Task 22)"""
        mode_frame = ctk.CTkFrame(self.content_frame)
        mode_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        mode_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            mode_frame, 
            text="Generation Mode:", 
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        # Radio buttons for operation modes
        self.mode_single = ctk.CTkRadioButton(
            mode_frame,
            text="Single Generation\nGenerate 1 or a few QR codes with same parameters",
            variable=self.operation_mode,
            value="single",
            font=ctk.CTkFont(size=12)
        )
        self.mode_single.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.mode_batch = ctk.CTkRadioButton(
            mode_frame,
            text="Batch Sequential Generation\nGenerate multiple QR codes with sequential numbering",
            variable=self.operation_mode,
            value="batch",
            font=ctk.CTkFont(size=12)
        )
        self.mode_batch.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        self.mode_csv = ctk.CTkRadioButton(
            mode_frame,
            text="CSV Import\nGenerate QR codes from data in a CSV file",
            variable=self.operation_mode,
            value="csv",
            font=ctk.CTkFont(size=12)
        )
        self.mode_csv.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        
        # Add some spacing
        mode_frame.grid_rowconfigure(2, minsize=15)
    
    def init_default_values(self):
        """Initialize default values for the form"""
        # Set default operation mode
        self.operation_mode.set("single")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
    def generate_qr_codes(self):
        """Main action - generate QR codes (placeholder for Task 30)"""
        selected_mode = self.operation_mode.get()
        mode_names = {"single": "Single Generation", "batch": "Batch Sequential", "csv": "CSV Import"}
        self.status_label.configure(text=f"Selected: {mode_names[selected_mode]} - Full integration coming in Task 30...")
        # TODO: Implement in Task 30 - Main window workflow integration
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point - now uses modern GUI instead of dialogs"""
    try:
        # Create and run the modern GUI
        app = QRGeneratorGUI()
        app.run()
    except Exception as e:
        # Fallback to old dialog-based interface if GUI fails
        print(f"GUI initialization failed: {e}")
        print("Falling back to dialog-based interface...")
        main_legacy()


def main_legacy():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Check if user wants to use presets
    use_presets = messagebox.askyesno("Presets", "Use parameter presets?\n\nYes = Manage presets\nNo = Enter parameters manually")
    
    loaded_preset = None
    if use_presets:
        choice, available_presets = show_preset_menu()
        
        if choice == "1" and available_presets:  # Load preset
            preset_name = simpledialog.askstring("Load Preset", f"Available presets: {', '.join(available_presets)}\n\nEnter preset name to load:")
            if preset_name:
                success, result = load_preset(preset_name)
                if success:
                    loaded_preset = result
                    messagebox.showinfo("Success", f"Preset '{preset_name}' loaded successfully!")
                else:
                    messagebox.showerror("Error", result)
                    return
        elif choice == "3" and available_presets:  # Delete preset
            preset_name = simpledialog.askstring("Delete Preset", f"Available presets: {', '.join(available_presets)}\n\nEnter preset name to delete:")
            if preset_name:
                success, result = delete_preset(preset_name)
                if success:
                    messagebox.showinfo("Success", result)
                else:
                    messagebox.showerror("Error", result)
                return
        # For choice "4" or "2", continue to parameter input

    # Ask user to choose operation mode (or use preset mode)
    if loaded_preset:
        batch_mode = loaded_preset["mode"] == "csv"
    else:
        batch_mode = messagebox.askyesno("Operation Mode", "Choose QR code generation mode:\n\nYes = Batch Generation (CSV file or multiple codes)\nNo = Single Generation (manual parameters)")
    
    if batch_mode:
        # Batch mode - ask for specific batch type
        csv_mode = messagebox.askyesno("Batch Mode", "Choose batch generation method:\n\nYes = Import from CSV file\nNo = Generate sequential codes with manual parameters")
    else:
        csv_mode = False
    
    if csv_mode:
        # CSV mode - get file and process it
        input_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if not input_file:
            messagebox.showerror("Error", "No file selected. Exiting.")
            return
        
        # Process CSV file
        try:
            # Use preset values or ask user for input
            if loaded_preset and loaded_preset["mode"] == "csv":
                delimiter = loaded_preset.get("delimiter", ",")
                input_column = loaded_preset.get("input_column", 0)
                skip_first_row = loaded_preset.get("skip_first_row", False)
                format = loaded_preset.get("format", "png")
                color = loaded_preset.get("color", "#000000")
                
                # Show loaded values to user for confirmation
                preset_info = f"Using preset values:\nDelimiter: {delimiter}\nColumn: {input_column}\nSkip first row: {skip_first_row}\nFormat: {format}\nColor: {color}"
                if not messagebox.askyesno("Preset Values", f"{preset_info}\n\nContinue with these values?"):
                    return
            else:
                detected_delimiter = detect_delimiter(input_file)
                delimiter = simpledialog.askstring("Input", f"Enter separator [{detected_delimiter}]:") or detected_delimiter
                input_column = simpledialog.askinteger("Input", "Enter 0-indexed input column [0]:", initialvalue=0)
                skip_first_row = messagebox.askyesno("Input", "Skip first row?")
                
                # Validate format
                format_input = simpledialog.askstring("Input", "Image format [png,svg]:", initialvalue="png")
                format_valid, format_result = validate_format(format_input)
                if not format_valid:
                    messagebox.showerror("Validation Error", format_result)
                    return
                format = format_result
                
                # Validate color
                color_input = simpledialog.askstring("Input", "Image color [hex or name]:", initialvalue="#000000")
                color_valid, color_result = validate_color_format(color_input)
                if not color_valid:
                    messagebox.showerror("Validation Error", color_result)
                    return
                color = color_result
            
            # Use preset values for advanced QR parameters or ask user
            if loaded_preset and loaded_preset["mode"] == "csv":
                qr_version = loaded_preset.get("qr_version", None)
                error_correction = loaded_preset.get("error_correction", "L")
                box_size = loaded_preset.get("box_size", 10)
                border = loaded_preset.get("border", 4)
                filename_prefix = loaded_preset.get("filename_prefix", "")
                filename_suffix = loaded_preset.get("filename_suffix", "")
                use_payload_as_filename = loaded_preset.get("use_payload_as_filename", True)
                png_quality = loaded_preset.get("png_quality", 85)
                svg_precision = loaded_preset.get("svg_precision", 2)
            else:
                # Ask for advanced QR code parameters
                advanced_qr = messagebox.askyesno("QR Parameters", "Configure advanced QR code parameters?")
                qr_version, error_correction, box_size, border = None, "L", 10, 4
                png_quality, svg_precision = 85, 2
                
                if advanced_qr:
                    # QR Version
                    version_input = simpledialog.askstring("QR Parameters", "QR version (1-40 or 'auto'):", initialvalue="auto")
                    version_valid, version_result = validate_qr_version(version_input)
                    if not version_valid:
                        messagebox.showerror("Validation Error", version_result)
                        return
                    qr_version = version_result
                    
                    # Error correction
                    error_input = simpledialog.askstring("QR Parameters", "Error correction level (L/M/Q/H):", initialvalue="L")
                    error_valid, error_result = validate_error_correction(error_input)
                    if not error_valid:
                        messagebox.showerror("Validation Error", error_result)
                        return
                    error_correction = error_result
                    
                    # Box size
                    box_size_input = simpledialog.askstring("QR Parameters", "Box size (pixels per module):", initialvalue="10")
                    box_size_valid, box_size_result = validate_integer_input(box_size_input, "Box size", 1, 50)
                    if not box_size_valid:
                        messagebox.showerror("Validation Error", box_size_result)
                        return
                    box_size = box_size_result
                    
                    # Border
                    border_input = simpledialog.askstring("QR Parameters", "Border size (modules):", initialvalue="4")
                    border_valid, border_result = validate_integer_input(border_input, "Border", 0, 20)
                    if not border_valid:
                        messagebox.showerror("Validation Error", border_result)
                        return
                    border = border_result
                    
                    # Format-specific options
                    if format == 'png':
                        quality_input = simpledialog.askstring("PNG Options", "PNG quality (0-100, higher is better):", initialvalue="85")
                        quality_valid, quality_result = validate_png_quality(quality_input)
                        if not quality_valid:
                            messagebox.showerror("Validation Error", quality_result)
                            return
                        png_quality = quality_result
                    elif format == 'svg':
                        precision_input = simpledialog.askstring("SVG Options", "SVG precision (decimal places 0-10):", initialvalue="2")
                        precision_valid, precision_result = validate_svg_precision(precision_input)
                        if not precision_valid:
                            messagebox.showerror("Validation Error", precision_result)
                            return
                        svg_precision = precision_result
                
                # Ask for filename customization options
                customize_filenames = messagebox.askyesno("Filename Options", "Customize filename format?")
                filename_prefix, filename_suffix, use_payload_as_filename = "", "", True
                
                if customize_filenames:
                    filename_prefix = simpledialog.askstring("Filename Options", "Enter filename prefix (optional):") or ""
                    filename_suffix = simpledialog.askstring("Filename Options", "Enter filename suffix (optional):") or ""
                    use_payload_as_filename = messagebox.askyesno("Filename Options", "Use CSV data as filename base?\n\nYes = Use data content\nNo = Use qr_code_1, qr_code_2, etc.")
            
            # Read CSV data
            with open(input_file, "r") as infile:
                reader = csv.reader(infile, delimiter=delimiter)
                if skip_first_row:
                    next(reader)
                rows = list(reader)
            
            if not rows:
                messagebox.showerror("Error", "No data found in CSV file.")
                return
                
            # Output directory selection
            use_custom_output = messagebox.askyesno("Output Directory", "Choose custom output directory?\n\nYes = Select directory\nNo = Use default 'output' folder")
            output_folder = "output"
            
            if use_custom_output:
                selected_dir = filedialog.askdirectory(title="Select Output Directory")
                if selected_dir:
                    output_folder = selected_dir
                else:
                    messagebox.showinfo("Info", "No directory selected. Using default 'output' folder.")
            
            zip_output = messagebox.askyesno("Input", "Add output files to a zip file?")
            zip_file_name = None
            if zip_output:
                zip_file_name = simpledialog.askstring("Input", f"Enter zip file name [output_{format}.zip]:", initialvalue=f"output_{format}.zip")
            
            # Ask if user wants to save current parameters as preset (only if not using existing preset)
            if not loaded_preset and use_presets and choice == "2":
                preset_name = simpledialog.askstring("Save Preset", "Enter name for this preset:")
                if preset_name:
                    preset_params = create_csv_mode_preset(
                        format, color, qr_version, error_correction, box_size, border,
                        filename_prefix, filename_suffix, use_payload_as_filename,
                        delimiter, input_column, skip_first_row, png_quality, svg_precision
                    )
                    success, result = save_preset(preset_name, preset_params)
                    if success:
                        messagebox.showinfo("Success", result)
                    else:
                        messagebox.showerror("Error", result)
            
            # For CSV mode, we don't use the sequential payload format, so we skip security_code and suffix_code
            # Generate QR codes from CSV data
            create_qr_codes(None, None, None, color, output_folder, format, None, csv_data=rows, input_column=input_column, qr_version=qr_version, error_correction=error_correction, box_size=box_size, border=border, filename_prefix=filename_prefix, filename_suffix=filename_suffix, use_payload_as_filename=use_payload_as_filename, png_quality=png_quality, svg_precision=svg_precision)
            
            messagebox.showinfo("Success", f"{len(rows)} QR codes generated successfully from CSV!")
            
            if zip_output:
                zip_output_files(output_folder, zip_file_name, format)
                
                # Ask about cleanup after zipping
                cleanup_files = messagebox.askyesno("File Cleanup", "Delete original files after zipping?\n\nYes = Keep only zip file\nNo = Keep both zip and original files")
                if cleanup_files:
                    clean_output_folder(output_folder)
            else:
                # No zip created, ask if user wants to clean up anyway (unusual but possible)
                cleanup_files = messagebox.askyesno("File Cleanup", "Delete generated files?\n\nYes = Delete all generated files\nNo = Keep generated files")
                if cleanup_files:
                    clean_output_folder(output_folder)
            return
            
        except FileNotFoundError:
            messagebox.showerror("Error", f"File '{input_file}' not found. Please check the filename and try again.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error processing CSV file: {e}")
            return
    
    elif batch_mode and not csv_mode:
        # Sequential batch mode - generate multiple QR codes with sequential parameters
        operation_title = "Batch Sequential Generation"
    else:
        # Single generation mode - generate one or a few QR codes
        operation_title = "Single QR Code Generation"
    
    # Manual parameter input mode (both single and sequential batch)
    # Use preset values or ask user for input
    if loaded_preset and loaded_preset["mode"] == "manual":
        valid_uses = loaded_preset.get("valid_uses", "15")
        volume = loaded_preset.get("volume", "500")
        end_date = loaded_preset.get("end_date", "26.12.31")
        color = loaded_preset.get("color", "#000000")
        format = loaded_preset.get("format", "png")
        security_code = loaded_preset.get("security_code", "SECD")
        suffix_code = loaded_preset.get("suffix_code", "23FF45EE")
        
        # Show loaded values to user for confirmation
        preset_info = f"Using preset values:\nValid uses: {valid_uses}\nVolume: {volume}\nEnd date: {end_date}\nColor: {color}\nFormat: {format}\nSecurity code: {security_code}\nSuffix code: {suffix_code}"
        if not messagebox.askyesno("Preset Values", f"{preset_info}\n\nContinue with these values?"):
            return
    else:
        # Validate valid_uses
        valid_uses_input = simpledialog.askstring(operation_title, "Enter Valid uses (e.g. 15):")
        if not valid_uses_input:
            messagebox.showerror("Error", "No valid uses entered. Exiting.")
            return
        
        valid_uses_valid, valid_uses_result = validate_integer_input(valid_uses_input, "Valid uses", 1, 9999)
        if not valid_uses_valid:
            messagebox.showerror("Validation Error", valid_uses_result)
            return
        valid_uses = str(valid_uses_result)

        # Validate volume
        volume_input = simpledialog.askstring(operation_title, "Enter Volume (e.g. 500):")
        if not volume_input:
            messagebox.showerror("Error", "No volume entered. Exiting.")
            return
        
        volume_valid, volume_result = validate_integer_input(volume_input, "Volume", 1, 99999)
        if not volume_valid:
            messagebox.showerror("Validation Error", volume_result)
            return
        volume = str(volume_result)

        # Validate end_date
        end_date_input = simpledialog.askstring(operation_title, "Enter Valid Until date:", initialvalue="26.12.31")
        if not end_date_input:
            messagebox.showerror("Error", "No end date entered. Exiting.")
            return
        
        date_valid, date_result = validate_date_format(end_date_input)
        if not date_valid:
            messagebox.showerror("Validation Error", date_result)
            return
        end_date = date_result

        # Validate color
        color_input = simpledialog.askstring(operation_title, "Image color [hex or name]:", initialvalue="#000000")
        color_valid, color_result = validate_color_format(color_input)
        if not color_valid:
            messagebox.showerror("Validation Error", color_result)
            return
        color = color_result
        
        # Validate format
        format_input = simpledialog.askstring(operation_title, "Image format [png,svg]:", initialvalue="png")
        format_valid, format_result = validate_format(format_input)
        if not format_valid:
            messagebox.showerror("Validation Error", format_result)
            return
        format = format_result
        
        # Ask for payload customization options
        security_code = simpledialog.askstring(operation_title, "Enter security code:", initialvalue="SECD")
        if not security_code:
            messagebox.showerror("Error", "No security code entered. Exiting.")
            return
        
        suffix_code = simpledialog.askstring(operation_title, "Enter suffix code:", initialvalue="23FF45EE")
        if not suffix_code:
            messagebox.showerror("Error", "No suffix code entered. Exiting.")
            return
    
    # Validate count (always ask this even with presets since it's generation specific)
    if batch_mode and not csv_mode:
        # Sequential batch mode - suggest more codes
        default_count = 10
        count_prompt = f"{operation_title} - How many sequential QR codes to generate?"
    else:
        # Single generation mode - suggest fewer codes
        default_count = 1
        count_prompt = f"{operation_title} - How many QR codes to generate?"
    
    count = simpledialog.askinteger(operation_title, count_prompt, initialvalue=default_count)
    if not count:
        messagebox.showerror("Error", "No count entered. Exiting.")
        return
    
    count_valid, count_result = validate_integer_input(count, "Count", 1, 10000)
    if not count_valid:
        messagebox.showerror("Validation Error", count_result)
        return
    count = count_result

    # Use preset values for advanced QR parameters or ask user
    if loaded_preset and loaded_preset["mode"] == "manual":
        qr_version = loaded_preset.get("qr_version", None)
        error_correction = loaded_preset.get("error_correction", "L")
        box_size = loaded_preset.get("box_size", 10)
        border = loaded_preset.get("border", 4)
        filename_prefix = loaded_preset.get("filename_prefix", "")
        filename_suffix = loaded_preset.get("filename_suffix", "")
        use_payload_as_filename = loaded_preset.get("use_payload_as_filename", True)
        png_quality = loaded_preset.get("png_quality", 85)
        svg_precision = loaded_preset.get("svg_precision", 2)
    else:
        # Ask for advanced QR code parameters
        advanced_qr = messagebox.askyesno(f"{operation_title} - QR Parameters", "Configure advanced QR code parameters?")
        qr_version, error_correction, box_size, border = None, "L", 10, 4
        png_quality, svg_precision = 85, 2
        
        if advanced_qr:
            # QR Version
            version_input = simpledialog.askstring(f"{operation_title} - QR Parameters", "QR version (1-40 or 'auto'):", initialvalue="auto")
            version_valid, version_result = validate_qr_version(version_input)
            if not version_valid:
                messagebox.showerror("Validation Error", version_result)
                return
            qr_version = version_result
            
            # Error correction
            error_input = simpledialog.askstring(f"{operation_title} - QR Parameters", "Error correction level (L/M/Q/H):", initialvalue="L")
            error_valid, error_result = validate_error_correction(error_input)
            if not error_valid:
                messagebox.showerror("Validation Error", error_result)
                return
            error_correction = error_result
            
            # Box size
            box_size_input = simpledialog.askstring(f"{operation_title} - QR Parameters", "Box size (pixels per module):", initialvalue="10")
            box_size_valid, box_size_result = validate_integer_input(box_size_input, "Box size", 1, 50)
            if not box_size_valid:
                messagebox.showerror("Validation Error", box_size_result)
                return
            box_size = box_size_result
            
            # Border
            border_input = simpledialog.askstring(f"{operation_title} - QR Parameters", "Border size (modules):", initialvalue="4")
            border_valid, border_result = validate_integer_input(border_input, "Border", 0, 20)
            if not border_valid:
                messagebox.showerror("Validation Error", border_result)
                return
            border = border_result
            
            # Format-specific options
            if format == 'png':
                quality_input = simpledialog.askstring(f"{operation_title} - PNG Options", "PNG quality (0-100, higher is better):", initialvalue="85")
                quality_valid, quality_result = validate_png_quality(quality_input)
                if not quality_valid:
                    messagebox.showerror("Validation Error", quality_result)
                    return
                png_quality = quality_result
            elif format == 'svg':
                precision_input = simpledialog.askstring(f"{operation_title} - SVG Options", "SVG precision (decimal places 0-10):", initialvalue="2")
                precision_valid, precision_result = validate_svg_precision(precision_input)
                if not precision_valid:
                    messagebox.showerror("Validation Error", precision_result)
                    return
                svg_precision = precision_result

        # Ask for filename customization options
        customize_filenames = messagebox.askyesno(f"{operation_title} - Filename Options", "Customize filename format?")
        filename_prefix, filename_suffix, use_payload_as_filename = "", "", True
        
        if customize_filenames:
            filename_prefix = simpledialog.askstring(f"{operation_title} - Filename Options", "Enter filename prefix (optional):") or ""
            filename_suffix = simpledialog.askstring(f"{operation_title} - Filename Options", "Enter filename suffix (optional):") or ""
            use_payload_as_filename = messagebox.askyesno(f"{operation_title} - Filename Options", "Use payload as filename base?\n\nYes = Use M-15-00000001-500-26.12.31-SECD-23FF45EE\nNo = Use qr_code_1, qr_code_2, etc.")

    # Output directory selection
    use_custom_output = messagebox.askyesno(f"{operation_title} - Output Directory", "Choose custom output directory?\n\nYes = Select directory\nNo = Use default 'output' folder")
    output_folder = "output"
    
    if use_custom_output:
        selected_dir = filedialog.askdirectory(title=f"Select Output Directory - {operation_title}")
        if selected_dir:
            output_folder = selected_dir
        else:
            messagebox.showinfo("Info", "No directory selected. Using default 'output' folder.")

    zip_output = messagebox.askyesno(f"{operation_title} - Output", "Add output files to a zip file?")
    zip_file_name = None
    if zip_output:
        zip_file_name = simpledialog.askstring(f"{operation_title} - Output", f"Enter zip file name:", initialvalue=f"QR-{valid_uses}-{volume}-{color}-{count}-{format}.zip")

    # Ask if user wants to save current parameters as preset (only if not using existing preset)
    if not loaded_preset and use_presets and choice == "2":
        preset_name = simpledialog.askstring("Save Preset", "Enter name for this preset:")
        if preset_name:
            preset_params = create_manual_mode_preset(
                valid_uses, volume, end_date, color, format, security_code, suffix_code,
                qr_version, error_correction, box_size, border,
                filename_prefix, filename_suffix, use_payload_as_filename,
                png_quality, svg_precision
            )
            success, result = save_preset(preset_name, preset_params)
            if success:
                messagebox.showinfo("Success", result)
            else:
                messagebox.showerror("Error", result)

    try:
        create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count, security_code=security_code, suffix_code=suffix_code, qr_version=qr_version, error_correction=error_correction, box_size=box_size, border=border, filename_prefix=filename_prefix, filename_suffix=filename_suffix, use_payload_as_filename=use_payload_as_filename, png_quality=png_quality, svg_precision=svg_precision)
        #messagebox.showinfo("Success", f"{count} QR codes generated successfully!")

        #if zip_output:
        zip_output_files(output_folder, zip_file_name, format)

        if zip_output and zip_file_name:
            # Ask about cleanup after zipping
            cleanup_files = messagebox.askyesno("File Cleanup", "Delete original files after zipping?\n\nYes = Keep only zip file\nNo = Keep both zip and original files")
            if cleanup_files:
                clean_output_folder(output_folder)
        else:
            # No zip created, ask if user wants to clean up anyway (unusual but possible)
            cleanup_files = messagebox.askyesno("File Cleanup", "Delete generated files?\n\nYes = Delete all generated files\nNo = Keep generated files")
            if cleanup_files:
                clean_output_folder(output_folder)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()
