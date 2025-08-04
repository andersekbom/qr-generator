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
        self.operation_mode = tk.StringVar(value="manual")  # manual, csv
        self.selected_preset = tk.StringVar(value="")
        self.csv_file_path = tk.StringVar(value="")
        
        # Parameter form variables
        self.valid_uses = tk.StringVar(value="15")
        self.volume = tk.StringVar(value="500")
        self.end_date = tk.StringVar(value="26.12.31")
        self.color = tk.StringVar(value="#000000")
        self.security_code = tk.StringVar(value="SECD")
        self.suffix_code = tk.StringVar(value="23FF45EE")
        self.count = tk.IntVar(value=1)
        
        # Format and advanced options variables
        self.format = tk.StringVar(value="png")
        self.png_quality = tk.IntVar(value=85)
        self.svg_precision = tk.IntVar(value=2)
        self.qr_version = tk.StringVar(value="auto")
        self.error_correction = tk.StringVar(value="L")
        self.box_size = tk.IntVar(value=10)
        self.border = tk.IntVar(value=4)
        
        # Filename customization variables (Task 27)
        self.filename_prefix = tk.StringVar(value="")
        self.filename_suffix = tk.StringVar(value="")
        self.use_payload_filename = tk.BooleanVar(value=True)
        
        # Output configuration variables
        self.output_directory = tk.StringVar(value="output")
        self.create_zip = tk.BooleanVar(value=True)
        self.zip_filename = tk.StringVar(value="")
        self.cleanup_files = tk.BooleanVar(value=False)
        self.cleanup_temp = tk.BooleanVar(value=False)
        
        # Create main layout
        self.create_main_layout()
        
        # Initialize with default values
        self.init_default_values()
        
        # Load saved configuration (Task 34)
        self.load_configuration()
        
        # Setup form validation
        self.setup_form_validation()
    
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
        
        # Menu bar (Task 33)
        self.create_menu_bar()
        
        # Header section
        self.create_header_section()
        
        # Main content area (scrollable)
        self.create_content_area()
        
        # Footer with action buttons
        self.create_footer_section()
        
        # Keyboard shortcuts (Task 33)
        self.setup_keyboard_shortcuts()
    
    def create_menu_bar(self):
        """Create menu bar with keyboard shortcuts (Task 33)"""
        try:
            # Create menu bar
            self.menubar = tk.Menu(self.root)
            self.root.configure(menu=self.menubar)
            
            # File menu
            file_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="New Session", command=self.new_session, accelerator="Ctrl+N")
            file_menu.add_separator()
            file_menu.add_command(label="Open CSV...", command=self.browse_csv_file, accelerator="Ctrl+O")
            file_menu.add_separator()
            file_menu.add_command(label="Generate QR Codes", command=self.generate_qr_codes, accelerator="Ctrl+G")
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
            
            # Edit menu
            edit_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Edit", menu=edit_menu)
            edit_menu.add_command(label="Clear Form", command=self.clear_form, accelerator="Ctrl+R")
            edit_menu.add_separator()
            edit_menu.add_command(label="Load Preset...", command=self.load_preset_dialog, accelerator="Ctrl+L")
            edit_menu.add_command(label="Save Preset...", command=self.save_preset_dialog, accelerator="Ctrl+S")
            
            # View menu
            view_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="View", menu=view_menu)
            view_menu.add_command(label="Toggle Theme", command=self.toggle_theme, accelerator="Ctrl+T")
            view_menu.add_separator()
            view_menu.add_command(label="Clear Results", command=self.clear_results, accelerator="Ctrl+Shift+C")
            view_menu.add_command(label="Open Output Folder", command=self.open_output_folder, accelerator="Ctrl+Shift+O")
            
            # Help menu
            help_menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="About", command=self.show_about, accelerator="F1")
            
        except Exception as e:
            print(f"Menu bar creation failed: {e}")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts (Task 33)"""
        try:
            # File shortcuts
            self.root.bind('<Control-n>', lambda e: self.new_session())
            self.root.bind('<Control-o>', lambda e: self.browse_csv_file())
            self.root.bind('<Control-g>', lambda e: self.generate_qr_codes())
            self.root.bind('<Control-q>', lambda e: self.root.quit())
            
            # Edit shortcuts
            self.root.bind('<Control-r>', lambda e: self.clear_form())
            self.root.bind('<Control-l>', lambda e: self.load_preset_dialog())
            self.root.bind('<Control-s>', lambda e: self.save_preset_dialog())
            
            # View shortcuts
            self.root.bind('<Control-t>', lambda e: self.toggle_theme())
            self.root.bind('<Control-Shift-C>', lambda e: self.clear_results())
            self.root.bind('<Control-Shift-O>', lambda e: self.open_output_folder())
            
            # Help shortcuts
            self.root.bind('<F1>', lambda e: self.show_about())
            
        except Exception as e:
            print(f"Keyboard shortcuts setup failed: {e}")
    
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
        
        # Preset Management Section (Task 23) - IMPLEMENTED
        self.create_preset_management_section()
        
        # CSV File Selection Section (Task 24) - IMPLEMENTED
        self.create_csv_file_section()
        
        # Parameter Input Forms Section (Task 25) - IMPLEMENTED
        self.create_parameter_forms_section()
        
        # Format and Advanced Options Section (Task 26) - IMPLEMENTED
        self.create_format_options_section()
        
        # Output Configuration Section (Task 28) - IMPLEMENTED
        self.create_output_config_section()
        
        # Results Viewer Section (Task 32) - IMPLEMENTED
        self.create_results_viewer_section()
        
        # Additional placeholder sections for other tasks
        # TODO: Task 27, 29-35 sections will be added here
    
    def create_results_viewer_section(self):
        """Create generation results viewer with thumbnails (Task 32)"""
        self.results_frame = ctk.CTkFrame(self.content_frame)
        self.results_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=10)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        self.results_title = ctk.CTkLabel(
            self.results_frame,
            text="Generation Results:",
            font=ctk.CTkFont(weight="bold", size=16)
        )
        self.results_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Results summary
        self.results_summary = ctk.CTkLabel(
            self.results_frame,
            text="No QR codes generated yet",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.results_summary.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        # Scrollable frame for thumbnails
        self.thumbnails_frame = ctk.CTkScrollableFrame(
            self.results_frame,
            height=200,
            orientation="horizontal"
        )
        self.thumbnails_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(self.results_frame)
        buttons_frame.grid(row=3, column=0, padx=20, pady=(0, 15), sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        # Open folder button
        self.open_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="Open Output Folder",
            width=150,
            command=self.open_output_folder,
            state="disabled"
        )
        self.open_folder_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Clear results button
        self.clear_results_btn = ctk.CTkButton(
            buttons_frame,
            text="Clear Results",
            width=120,
            command=self.clear_results,
            fg_color="gray",
            hover_color="darkgray",
            state="disabled"
        )
        self.clear_results_btn.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Initially hide the results section
        self.results_frame.grid_remove()
    
    def create_footer_section(self):
        """Create footer with main action buttons"""
        footer_frame = ctk.CTkFrame(self.root)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Generate button (starts disabled until form is valid)
        self.generate_button = ctk.CTkButton(
            footer_frame,
            text="Generate QR Codes",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=40,
            command=self.generate_qr_codes,
            state="disabled"
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
        self.mode_manual = ctk.CTkRadioButton(
            mode_frame,
            text="Manual Generation\nGenerate QR codes with sequential serials (set count: 1 for single, multiple for batch)",
            variable=self.operation_mode,
            value="manual",
            font=ctk.CTkFont(size=12),
            command=self.on_mode_change
        )
        self.mode_manual.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.mode_csv = ctk.CTkRadioButton(
            mode_frame,
            text="CSV Import\nGenerate QR codes from data in a CSV file",
            variable=self.operation_mode,
            value="csv",
            font=ctk.CTkFont(size=12),
            command=self.on_mode_change
        )
        self.mode_csv.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        # Add some spacing
        mode_frame.grid_rowconfigure(2, minsize=15)
    
    def create_preset_management_section(self):
        """Create preset management with dropdown and buttons (Task 23)"""
        preset_frame = ctk.CTkFrame(self.content_frame)
        preset_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        preset_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            preset_frame, 
            text="Parameter Presets:", 
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")
        
        # Preset dropdown
        self.preset_dropdown = ctk.CTkComboBox(
            preset_frame,
            variable=self.selected_preset,
            values=self.get_available_presets(),
            state="readonly",
            width=200
        )
        self.preset_dropdown.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        # Management buttons
        self.load_preset_btn = ctk.CTkButton(
            preset_frame,
            text="Load",
            width=80,
            command=self.load_selected_preset
        )
        self.load_preset_btn.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        self.save_preset_btn = ctk.CTkButton(
            preset_frame,
            text="Save New",
            width=80,
            command=self.save_new_preset
        )
        self.save_preset_btn.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        self.delete_preset_btn = ctk.CTkButton(
            preset_frame,
            text="Delete",
            width=80,
            command=self.delete_selected_preset,
            fg_color="darkred",
            hover_color="red"
        )
        self.delete_preset_btn.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Status label for preset operations
        self.preset_status = ctk.CTkLabel(
            preset_frame,
            text="Select a preset to load saved parameters",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        self.preset_status.grid(row=2, column=0, columnspan=4, padx=20, pady=(5, 15), sticky="w")
    
    def get_available_presets(self):
        """Get list of available preset names"""
        try:
            preset_dir = "presets"
            if os.path.exists(preset_dir):
                presets = [f[:-5] for f in os.listdir(preset_dir) if f.endswith('.json')]
                return ["Select preset..."] + sorted(presets)
            return ["Select preset..."]
        except Exception:
            return ["Select preset..."]
    
    def refresh_preset_list(self):
        """Refresh the preset dropdown list"""
        self.preset_dropdown.configure(values=self.get_available_presets())
    
    def load_selected_preset(self):
        """Load the selected preset from dropdown"""
        preset_name = self.selected_preset.get()
        if preset_name and preset_name != "Select preset...":
            success, result = load_preset(preset_name)
            if success:
                self.preset_status.configure(text=f"✅ Loaded preset: {preset_name}", text_color="green")
                # TODO: Task 30 - Apply preset values to form fields
            else:
                self.preset_status.configure(text=f"❌ Error: {result}", text_color="red")
        else:
            self.preset_status.configure(text="Please select a preset first", text_color="orange")
    
    def save_new_preset(self):
        """Save current form values as new preset"""
        # Create dialog for preset name
        dialog = ctk.CTkInputDialog(text="Enter name for new preset:", title="Save Preset")
        preset_name = dialog.get_input()
        
        if preset_name:
            # TODO: Task 30 - Collect current form values
            # For now, create a sample preset structure
            preset_params = {
                "mode": self.operation_mode.get(),
                "created": "GUI v2.0"
            }
            
            success, result = save_preset(preset_name, preset_params)
            if success:
                self.preset_status.configure(text=f"✅ Saved preset: {preset_name}", text_color="green")
                self.refresh_preset_list()
                self.selected_preset.set(preset_name)
            else:
                self.preset_status.configure(text=f"❌ Error: {result}", text_color="red")
        else:
            self.preset_status.configure(text="Save cancelled", text_color="gray")
    
    def delete_selected_preset(self):
        """Delete the selected preset"""
        preset_name = self.selected_preset.get()
        if preset_name and preset_name != "Select preset...":
            # Confirmation dialog
            dialog = ctk.CTkInputDialog(
                text=f"Type 'DELETE' to confirm deletion of preset '{preset_name}':", 
                title="Confirm Deletion"
            )
            confirm = dialog.get_input()
            
            if confirm == "DELETE":
                success, result = delete_preset(preset_name)
                if success:
                    self.preset_status.configure(text=f"✅ Deleted preset: {preset_name}", text_color="green")
                    self.refresh_preset_list()
                    self.selected_preset.set("Select preset...")
                else:
                    self.preset_status.configure(text=f"❌ Error: {result}", text_color="red")
            else:
                self.preset_status.configure(text="Deletion cancelled", text_color="gray")
        else:
            self.preset_status.configure(text="Please select a preset to delete", text_color="orange")
    
    def create_csv_file_section(self):
        """Create CSV file selection widget with browse button (Task 24)"""
        self.csv_frame = ctk.CTkFrame(self.content_frame)
        self.csv_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.csv_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            self.csv_frame, 
            text="CSV File Selection:", 
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10), sticky="w")
        
        # File path display
        self.csv_path_entry = ctk.CTkEntry(
            self.csv_frame,
            textvariable=self.csv_file_path,
            placeholder_text="No CSV file selected...",
            state="readonly",
            width=400
        )
        self.csv_path_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Browse button
        self.browse_csv_btn = ctk.CTkButton(
            self.csv_frame,
            text="Browse CSV",
            width=120,
            command=self.browse_csv_file
        )
        self.browse_csv_btn.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Clear button
        self.clear_csv_btn = ctk.CTkButton(
            self.csv_frame,
            text="Clear",
            width=80,
            command=self.clear_csv_file,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_csv_btn.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        # CSV options sub-section
        csv_options_frame = ctk.CTkFrame(self.csv_frame)
        csv_options_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=15, pady=(10, 15))
        csv_options_frame.grid_columnconfigure(1, weight=1)
        
        # Delimiter detection display
        ctk.CTkLabel(csv_options_frame, text="Detected delimiter:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=15, pady=8, sticky="w")
        
        self.delimiter_label = ctk.CTkLabel(
            csv_options_frame, 
            text="(will detect when file selected)",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        self.delimiter_label.grid(row=0, column=1, padx=15, pady=8, sticky="w")
        
        # Column selection
        ctk.CTkLabel(csv_options_frame, text="Data column:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, padx=15, pady=8, sticky="w")
        
        self.csv_column = tk.IntVar(value=0)
        self.column_spinbox = ctk.CTkEntry(
            csv_options_frame,
            width=80,
            placeholder_text="0"
        )
        self.column_spinbox.grid(row=1, column=1, padx=15, pady=8, sticky="w")
        
        # Header skip option
        self.skip_header = tk.BooleanVar(value=False)
        self.header_checkbox = ctk.CTkCheckBox(
            csv_options_frame,
            text="Skip first row (header)",
            variable=self.skip_header,
            font=ctk.CTkFont(size=12)
        )
        self.header_checkbox.grid(row=2, column=0, columnspan=2, padx=15, pady=8, sticky="w")
        
        # CSV Preview Table (Task 31)
        self.create_csv_preview_table()
        
        # Initially hide the CSV section (show only when CSV mode selected)
        self.csv_frame.grid_remove()
    
    def create_csv_preview_table(self):
        """Create CSV preview and column selection table (Task 31)"""
        # Preview frame
        preview_frame = ctk.CTkFrame(self.csv_frame)
        preview_frame.grid(row=4, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview title
        ctk.CTkLabel(
            preview_frame,
            text="CSV Preview:",
            font=ctk.CTkFont(weight="bold", size=14)
        ).grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # Create Treeview for table display
        try:
            import tkinter.ttk as ttk
            
            # Style the treeview to match CustomTkinter theme
            style = ttk.Style()
            
            # Table frame with scrollbars
            table_frame = tk.Frame(preview_frame, bg=preview_frame.cget("fg_color")[1])
            table_frame.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")
            table_frame.grid_columnconfigure(0, weight=1)
            
            # Create treeview with scrollbars
            self.csv_tree = ttk.Treeview(table_frame, height=8, show='tree headings')
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.csv_tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.csv_tree.xview)
            
            self.csv_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Grid layout
            self.csv_tree.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            # Configure grid weights
            table_frame.grid_rowconfigure(0, weight=1)
            table_frame.grid_columnconfigure(0, weight=1)
            
            # Column selection info
            self.column_info_label = ctk.CTkLabel(
                preview_frame,
                text="Select column above or click column header to use as QR data",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            self.column_info_label.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="w")
            
            # Bind column selection
            self.csv_tree.bind('<Button-1>', self.on_column_select)
            
        except ImportError:
            # Fallback if ttk is not available
            fallback_label = ctk.CTkLabel(
                preview_frame,
                text="CSV preview not available (requires tkinter.ttk)",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            fallback_label.grid(row=1, column=0, padx=15, pady=15)
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file"""
        try:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            
            if file_path:
                self.csv_file_path.set(file_path)
                self.detect_csv_properties(file_path)
                # Trigger validation after CSV file selection
                self.validate_form()
        except Exception as e:
            self.preset_status.configure(text=f"❌ Error selecting file: {e}", text_color="red")
    
    def clear_csv_file(self):
        """Clear the selected CSV file"""
        self.csv_file_path.set("")
        self.delimiter_label.configure(text="(will detect when file selected)", text_color="gray")
        self.column_spinbox.delete(0, 'end')
        self.column_spinbox.insert(0, "0")
        self.skip_header.set(False)
    
    def detect_csv_properties(self, file_path):
        """Detect and display CSV file properties"""
        try:
            # Use existing detect_delimiter function
            detected_delimiter = detect_delimiter(file_path)
            
            # Display delimiter in a user-friendly way
            delimiter_names = {
                ',': 'comma (,)',
                ';': 'semicolon (;)',
                '\t': 'tab',
                '|': 'pipe (|)'
            }
            delimiter_display = delimiter_names.get(detected_delimiter, f"'{detected_delimiter}'")
            
            self.delimiter_label.configure(
                text=delimiter_display, 
                text_color="green"
            )
            
            # Load and display CSV preview
            self.load_csv_preview(file_path, detected_delimiter)
            
        except Exception as e:
            self.delimiter_label.configure(
                text=f"Error: {str(e)}", 
                text_color="red"
            )
    
    def load_csv_preview(self, file_path, delimiter):
        """Load CSV data into preview table (Task 31)"""
        try:
            if not hasattr(self, 'csv_tree'):
                return
                
            import csv
            
            # Clear existing data
            for item in self.csv_tree.get_children():
                self.csv_tree.delete(item)
            
            # Read CSV file
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                return
            
            # Setup columns based on first row
            first_row = rows[0]
            num_columns = len(first_row)
            
            # Configure treeview columns
            columns = [f"col_{i}" for i in range(num_columns)]
            self.csv_tree['columns'] = columns
            self.csv_tree['show'] = 'headings'
            
            # Setup column headers and widths
            for i, col in enumerate(columns):
                header = f"Column {i}" if len(first_row[i]) > 20 else first_row[i]
                self.csv_tree.heading(col, text=header, command=lambda c=i: self.select_column(c))
                self.csv_tree.column(col, width=150, anchor='w')
            
            # Add data (limit to first 20 rows for performance)
            max_rows = min(20, len(rows))
            for row_idx, row in enumerate(rows[:max_rows]):
                # Pad row if it has fewer columns than expected
                padded_row = row + [''] * (num_columns - len(row))
                padded_row = padded_row[:num_columns]  # Truncate if too many columns
                
                # Truncate long cell values for display
                display_row = [cell[:50] + '...' if len(cell) > 50 else cell for cell in padded_row]
                
                self.csv_tree.insert('', 'end', values=display_row)
            
            # Update info label
            total_rows = len(rows)
            self.column_info_label.configure(
                text=f"Showing {max_rows} of {total_rows} rows. Click column header to select for QR data."
            )
            
        except Exception as e:
            if hasattr(self, 'column_info_label'):
                self.column_info_label.configure(text=f"Error loading preview: {str(e)}")
    
    def on_column_select(self, event):
        """Handle column selection from table click (Task 31)"""
        try:
            if not hasattr(self, 'csv_tree'):
                return
                
            # Get the clicked column
            region = self.csv_tree.identify_region(event.x, event.y)
            if region == "heading":
                column = self.csv_tree.identify_column(event.x, event.y)
                if column:
                    # Column IDs are like '#1', '#2', etc.
                    col_index = int(column.replace('#', '')) - 1
                    self.select_column(col_index)
        except Exception:
            pass  # Ignore click handling errors
    
    def select_column(self, column_index):
        """Select a column for QR data generation (Task 31)"""
        try:
            # Update the column spinbox
            self.column_spinbox.delete(0, 'end')
            self.column_spinbox.insert(0, str(column_index))
            self.csv_column.set(column_index)
            
            # Update info label
            self.column_info_label.configure(
                text=f"Selected column {column_index} for QR code data",
                text_color="green"
            )
            
        except Exception as e:
            if hasattr(self, 'column_info_label'):
                self.column_info_label.configure(text=f"Error selecting column: {str(e)}")
    
    def show_csv_section(self, show=True):
        """Show or hide the CSV file selection section"""
        if show:
            self.csv_frame.grid()
        else:
            self.csv_frame.grid_remove()
    
    def on_mode_change(self):
        """Handle operation mode changes to show/hide relevant sections"""
        mode = self.operation_mode.get()
        
        # Show/hide sections based on mode
        if mode == "csv":
            self.show_csv_section(True)
            self.show_parameter_section(False)
            self.show_format_section(True)  # CSV mode also needs format options
            self.show_output_section(True)  # All modes need output options
            self.status_label.configure(text="CSV mode selected - choose a CSV file to import data")
            # Trigger validation after mode change
            self.validate_form()
        elif mode == "manual":
            self.show_csv_section(False)
            self.show_parameter_section(True)
            self.show_format_section(True)  # Manual mode needs format options
            self.show_output_section(True)  # All modes need output options
            self.status_label.configure(text="Manual mode selected - enter QR code parameters (set count: 1 for single, multiple for batch)")
            # Trigger validation after mode change
            self.validate_form()
    
    def create_parameter_forms_section(self):
        """Create parameter input forms with validation (Task 25)"""
        self.params_frame = ctk.CTkFrame(self.content_frame)
        self.params_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        self.params_frame.grid_columnconfigure(1, weight=1)
        self.params_frame.grid_columnconfigure(3, weight=1)
        
        # Section title
        ctk.CTkLabel(
            self.params_frame, 
            text="QR Code Parameters:", 
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")
        
        # Row 1: Valid Uses and Volume
        ctk.CTkLabel(self.params_frame, text="Valid Uses:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, padx=20, pady=8, sticky="w")
        
        self.valid_uses_entry = ctk.CTkEntry(
            self.params_frame,
            textvariable=self.valid_uses,
            width=100,
            placeholder_text="15"
        )
        self.valid_uses_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        ctk.CTkLabel(self.params_frame, text="Volume:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=2, padx=20, pady=8, sticky="w")
        
        self.volume_entry = ctk.CTkEntry(
            self.params_frame,
            textvariable=self.volume,
            width=100,
            placeholder_text="500"
        )
        self.volume_entry.grid(row=1, column=3, padx=10, pady=8, sticky="w")
        
        # Row 2: End Date and Color
        ctk.CTkLabel(self.params_frame, text="Valid Until:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, padx=20, pady=8, sticky="w")
        
        self.end_date_entry = ctk.CTkEntry(
            self.params_frame,
            textvariable=self.end_date,
            width=100,
            placeholder_text="DD.MM.YY"
        )
        self.end_date_entry.grid(row=2, column=1, padx=10, pady=8, sticky="w")
        
        ctk.CTkLabel(self.params_frame, text="Color:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=2, padx=20, pady=8, sticky="w")
        
        color_frame = ctk.CTkFrame(self.params_frame)
        color_frame.grid(row=2, column=3, padx=10, pady=8, sticky="w")
        
        self.color_entry = ctk.CTkEntry(
            color_frame,
            textvariable=self.color,
            width=100,
            placeholder_text="#000000"
        )
        self.color_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.color_preview = ctk.CTkButton(
            color_frame,
            text="",
            width=30,
            height=30,
            fg_color=self.color.get(),
            command=self.choose_color
        )
        self.color_preview.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Row 3: Security Code and Suffix Code
        ctk.CTkLabel(self.params_frame, text="Security Code:", font=ctk.CTkFont(size=12)).grid(
            row=3, column=0, padx=20, pady=8, sticky="w")
        
        self.security_entry = ctk.CTkEntry(
            self.params_frame,
            textvariable=self.security_code,
            width=100,
            placeholder_text="SECD"
        )
        self.security_entry.grid(row=3, column=1, padx=10, pady=8, sticky="w")
        
        ctk.CTkLabel(self.params_frame, text="Suffix Code:", font=ctk.CTkFont(size=12)).grid(
            row=3, column=2, padx=20, pady=8, sticky="w")
        
        self.suffix_entry = ctk.CTkEntry(
            self.params_frame,
            textvariable=self.suffix_code,
            width=100,
            placeholder_text="23FF45EE"
        )
        self.suffix_entry.grid(row=3, column=3, padx=10, pady=8, sticky="w")
        
        # Row 4: Count
        ctk.CTkLabel(self.params_frame, text="Count:", font=ctk.CTkFont(size=12)).grid(
            row=4, column=0, padx=20, pady=8, sticky="w")
        
        count_frame = ctk.CTkFrame(self.params_frame)
        count_frame.grid(row=4, column=1, padx=10, pady=8, sticky="w")
        
        self.count_entry = ctk.CTkEntry(
            count_frame,
            width=80,
            placeholder_text="1"
        )
        self.count_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Count adjustment buttons
        self.count_minus_btn = ctk.CTkButton(
            count_frame,
            text="-",
            width=30,
            command=self.decrease_count
        )
        self.count_minus_btn.grid(row=0, column=1, padx=2, pady=5, sticky="w")
        
        self.count_plus_btn = ctk.CTkButton(
            count_frame,
            text="+",
            width=30,
            command=self.increase_count
        )
        self.count_plus_btn.grid(row=0, column=2, padx=2, pady=5, sticky="w")
        
        # Validation status
        self.param_status = ctk.CTkLabel(
            self.params_frame,
            text="Enter parameters for QR code generation",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        self.param_status.grid(row=5, column=0, columnspan=4, padx=20, pady=(5, 15), sticky="w")
        
        # Initially hide the parameter section (show only for single/batch modes)
        self.params_frame.grid_remove()
    
    def choose_color(self):
        """Open color picker dialog"""
        try:
            from tkinter import colorchooser
            color = colorchooser.askcolor(color=self.color.get())
            if color[1]:  # color[1] is the hex string
                self.color.set(color[1])
                self.color_preview.configure(fg_color=color[1])
        except Exception as e:
            self.param_status.configure(text=f"❌ Color picker error: {e}", text_color="red")
    
    def increase_count(self):
        """Increase count value"""
        try:
            current = int(self.count_entry.get() or "1")
            if current < 10000:
                new_value = current + 1
                self.count_entry.delete(0, 'end')
                self.count_entry.insert(0, str(new_value))
                self.count.set(new_value)
        except ValueError:
            self.count_entry.delete(0, 'end')
            self.count_entry.insert(0, "1")
            self.count.set(1)
    
    def decrease_count(self):
        """Decrease count value"""
        try:
            current = int(self.count_entry.get() or "1")
            if current > 1:
                new_value = current - 1
                self.count_entry.delete(0, 'end')
                self.count_entry.insert(0, str(new_value))
                self.count.set(new_value)
        except ValueError:
            self.count_entry.delete(0, 'end')
            self.count_entry.insert(0, "1")
            self.count.set(1)
    
    def show_parameter_section(self, show=True):
        """Show or hide the parameter forms section"""
        if show:
            self.params_frame.grid()
        else:
            self.params_frame.grid_remove()
    
    def create_format_options_section(self):
        """Create format and advanced options panel (Task 26)"""
        self.format_frame = ctk.CTkFrame(self.content_frame)
        self.format_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        self.format_frame.grid_columnconfigure(1, weight=1)
        self.format_frame.grid_columnconfigure(3, weight=1)
        
        # Section title
        ctk.CTkLabel(
            self.format_frame, 
            text="Format & Advanced Options:", 
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")
        
        # Format selection
        format_selection_frame = ctk.CTkFrame(self.format_frame)
        format_selection_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 10))
        
        ctk.CTkLabel(format_selection_frame, text="Output Format:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=15, pady=8, sticky="w")
        
        # Format radio buttons
        self.format_png = ctk.CTkRadioButton(
            format_selection_frame,
            text="PNG (Raster Image)",
            variable=self.format,
            value="png",
            command=self.on_format_change
        )
        self.format_png.grid(row=0, column=1, padx=20, pady=8, sticky="w")
        
        self.format_svg = ctk.CTkRadioButton(
            format_selection_frame,
            text="SVG (Vector Image)",
            variable=self.format,
            value="svg",
            command=self.on_format_change
        )
        self.format_svg.grid(row=0, column=2, padx=20, pady=8, sticky="w")
        
        # Format-specific options frame
        self.format_specific_frame = ctk.CTkFrame(self.format_frame)
        self.format_specific_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 10))
        self.format_specific_frame.grid_columnconfigure(1, weight=1)
        
        # PNG Quality slider (initially visible)
        self.png_quality_label = ctk.CTkLabel(self.format_specific_frame, text="PNG Quality:", font=ctk.CTkFont(size=12))
        self.png_quality_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        self.png_quality_slider = ctk.CTkSlider(
            self.format_specific_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            variable=self.png_quality,
            command=self.update_png_quality_label
        )
        self.png_quality_slider.grid(row=0, column=1, padx=15, pady=8, sticky="ew")
        
        self.png_quality_value = ctk.CTkLabel(self.format_specific_frame, text="85", font=ctk.CTkFont(size=12))
        self.png_quality_value.grid(row=0, column=2, padx=15, pady=8, sticky="w")
        
        # SVG Precision slider (initially hidden)
        self.svg_precision_label = ctk.CTkLabel(self.format_specific_frame, text="SVG Precision:", font=ctk.CTkFont(size=12))
        self.svg_precision_slider = ctk.CTkSlider(
            self.format_specific_frame,
            from_=0,
            to=10,
            number_of_steps=10,
            variable=self.svg_precision,
            command=self.update_svg_precision_label
        )
        self.svg_precision_value = ctk.CTkLabel(self.format_specific_frame, text="2", font=ctk.CTkFont(size=12))
        
        # Advanced QR Options frame
        self.advanced_frame = ctk.CTkFrame(self.format_frame)
        self.advanced_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 10))
        self.advanced_frame.grid_columnconfigure(1, weight=1)
        self.advanced_frame.grid_columnconfigure(3, weight=1)
        
        # Advanced options toggle
        self.show_advanced = tk.BooleanVar(value=False)
        self.advanced_toggle = ctk.CTkCheckBox(
            self.advanced_frame,
            text="Show Advanced QR Code Options",
            variable=self.show_advanced,
            command=self.toggle_advanced_options,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.advanced_toggle.grid(row=0, column=0, columnspan=4, padx=15, pady=8, sticky="w")
        
        # Advanced options content (initially hidden)
        self.advanced_content = ctk.CTkFrame(self.advanced_frame)
        
        # QR Version
        ctk.CTkLabel(self.advanced_content, text="QR Version:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=0, padx=15, pady=8, sticky="w")
        
        self.qr_version_combo = ctk.CTkComboBox(
            self.advanced_content,
            variable=self.qr_version,
            values=["auto"] + [str(i) for i in range(1, 41)],
            width=80
        )
        self.qr_version_combo.grid(row=1, column=1, padx=15, pady=8, sticky="w")
        
        # Error Correction
        ctk.CTkLabel(self.advanced_content, text="Error Correction:", font=ctk.CTkFont(size=12)).grid(
            row=1, column=2, padx=15, pady=8, sticky="w")
        
        self.error_correction_combo = ctk.CTkComboBox(
            self.advanced_content,
            variable=self.error_correction,
            values=["L", "M", "Q", "H"],
            width=80
        )
        self.error_correction_combo.grid(row=1, column=3, padx=15, pady=8, sticky="w")
        
        # Box Size
        ctk.CTkLabel(self.advanced_content, text="Box Size:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, padx=15, pady=8, sticky="w")
        
        self.box_size_slider = ctk.CTkSlider(
            self.advanced_content,
            from_=1,
            to=50,
            number_of_steps=49,
            variable=self.box_size,
            command=self.update_box_size_label
        )
        self.box_size_slider.grid(row=2, column=1, padx=15, pady=8, sticky="ew")
        
        self.box_size_value = ctk.CTkLabel(self.advanced_content, text="10", font=ctk.CTkFont(size=12))
        self.box_size_value.grid(row=2, column=2, padx=15, pady=8, sticky="w")
        
        # Border Size
        ctk.CTkLabel(self.advanced_content, text="Border:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=3, padx=15, pady=8, sticky="w")
        
        border_frame = ctk.CTkFrame(self.advanced_content)
        border_frame.grid(row=2, column=3, padx=15, pady=8, sticky="w")
        
        self.border_slider = ctk.CTkSlider(
            border_frame,
            from_=0,
            to=20,
            number_of_steps=20,
            variable=self.border,
            command=self.update_border_label,
            width=80
        )
        self.border_slider.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.border_value = ctk.CTkLabel(border_frame, text="4", font=ctk.CTkFont(size=12))
        self.border_value.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Initially hide the parameter section and advanced options
        self.format_frame.grid_remove()
    
    def on_format_change(self):
        """Handle format selection changes to show format-specific options"""
        format_type = self.format.get()
        
        # Hide all format-specific options first
        self.png_quality_label.grid_remove()
        self.png_quality_slider.grid_remove()
        self.png_quality_value.grid_remove()
        self.svg_precision_label.grid_remove()
        self.svg_precision_slider.grid_remove()
        self.svg_precision_value.grid_remove()
        
        # Show relevant format-specific options
        if format_type == "png":
            self.png_quality_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
            self.png_quality_slider.grid(row=0, column=1, padx=15, pady=8, sticky="ew")
            self.png_quality_value.grid(row=0, column=2, padx=15, pady=8, sticky="w")
        elif format_type == "svg":
            self.svg_precision_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
            self.svg_precision_slider.grid(row=0, column=1, padx=15, pady=8, sticky="ew")
            self.svg_precision_value.grid(row=0, column=2, padx=15, pady=8, sticky="w")
    
    def toggle_advanced_options(self):
        """Show or hide advanced QR code options"""
        if self.show_advanced.get():
            self.advanced_content.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=(5, 10))
            self.advanced_content.grid_columnconfigure(1, weight=1)
            self.advanced_content.grid_columnconfigure(3, weight=1)
        else:
            self.advanced_content.grid_remove()
    
    def update_png_quality_label(self, value):
        """Update PNG quality label with current value"""
        self.png_quality_value.configure(text=str(int(float(value))))
    
    def update_svg_precision_label(self, value):
        """Update SVG precision label with current value"""
        self.svg_precision_value.configure(text=str(int(float(value))))
    
    def update_box_size_label(self, value):
        """Update box size label with current value"""
        self.box_size_value.configure(text=str(int(float(value))))
    
    def update_border_label(self, value):
        """Update border label with current value"""
        self.border_value.configure(text=str(int(float(value))))
    
    def show_format_section(self, show=True):
        """Show or hide the format and advanced options section"""
        if show:
            self.format_frame.grid()
        else:
            self.format_frame.grid_remove()
    
    def create_output_config_section(self):
        """Create output configuration panel (Task 28)"""
        self.output_frame = ctk.CTkFrame(self.content_frame)
        self.output_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=10)
        self.output_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        ctk.CTkLabel(
            self.output_frame, 
            text="Output Configuration:", 
            font=ctk.CTkFont(weight="bold", size=16)
        ).grid(row=0, column=0, columnspan=4, padx=20, pady=(15, 10), sticky="w")
        
        # Output directory selection
        output_dir_frame = ctk.CTkFrame(self.output_frame)
        output_dir_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 10))
        output_dir_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(output_dir_frame, text="Output Directory:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=15, pady=8, sticky="w")
        
        self.output_dir_entry = ctk.CTkEntry(
            output_dir_frame,
            textvariable=self.output_directory,
            placeholder_text="output",
            width=300
        )
        self.output_dir_entry.grid(row=0, column=1, padx=15, pady=8, sticky="ew")
        
        self.browse_output_btn = ctk.CTkButton(
            output_dir_frame,
            text="Browse",
            width=80,
            command=self.browse_output_directory
        )
        self.browse_output_btn.grid(row=0, column=2, padx=10, pady=8, sticky="w")
        
        self.reset_output_btn = ctk.CTkButton(
            output_dir_frame,
            text="Reset",
            width=60,
            command=self.reset_output_directory,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.reset_output_btn.grid(row=0, column=3, padx=10, pady=8, sticky="w")
        
        # ZIP file options
        zip_frame = ctk.CTkFrame(self.output_frame)
        zip_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 10))
        zip_frame.grid_columnconfigure(1, weight=1)
        
        self.zip_checkbox = ctk.CTkCheckBox(
            zip_frame,
            text="Create ZIP file",
            variable=self.create_zip,
            command=self.on_zip_toggle,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.zip_checkbox.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        # ZIP filename entry (initially visible since create_zip defaults to True)
        zip_name_frame = ctk.CTkFrame(zip_frame)
        zip_name_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=(5, 10))
        zip_name_frame.grid_columnconfigure(1, weight=1)
        
        self.zip_filename_label = ctk.CTkLabel(zip_name_frame, text="ZIP filename:", font=ctk.CTkFont(size=12))
        self.zip_filename_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        self.zip_filename_entry = ctk.CTkEntry(
            zip_name_frame,
            textvariable=self.zip_filename,
            placeholder_text="auto-generated based on parameters",
            width=250
        )
        self.zip_filename_entry.grid(row=0, column=1, padx=15, pady=8, sticky="ew")
        
        self.auto_zip_btn = ctk.CTkButton(
            zip_name_frame,
            text="Auto",
            width=60,
            command=self.generate_auto_zip_name,
            fg_color="darkblue",
            hover_color="blue"
        )
        self.auto_zip_btn.grid(row=0, column=2, padx=10, pady=8, sticky="w")
        
        self.zip_name_frame = zip_name_frame  # Store reference for show/hide
        
        # File cleanup options
        cleanup_frame = ctk.CTkFrame(self.output_frame)
        cleanup_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=15, pady=(5, 15))
        
        self.cleanup_checkbox = ctk.CTkCheckBox(
            cleanup_frame,
            text="Delete original files after ZIP creation (keep only ZIP file)",
            variable=self.cleanup_files,
            font=ctk.CTkFont(size=12)
        )
        self.cleanup_checkbox.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        # Output status
        self.output_status = ctk.CTkLabel(
            self.output_frame,
            text="Files will be saved to the output directory",
            text_color="gray",
            font=ctk.CTkFont(size=11)
        )
        self.output_status.grid(row=4, column=0, columnspan=4, padx=20, pady=(5, 15), sticky="w")
        
        # Initially hide the output section
        self.output_frame.grid_remove()
    
    def browse_output_directory(self):
        """Open directory dialog to select output directory"""
        try:
            from tkinter import filedialog
            directory = filedialog.askdirectory(
                title="Select Output Directory",
                initialdir=self.output_directory.get()
            )
            
            if directory:
                self.output_directory.set(directory)
                self.output_status.configure(
                    text=f"✅ Output directory: {directory}",
                    text_color="green"
                )
        except Exception as e:
            self.output_status.configure(
                text=f"❌ Error selecting directory: {e}",
                text_color="red"
            )
    
    def reset_output_directory(self):
        """Reset output directory to default"""
        self.output_directory.set("output")
        self.output_status.configure(
            text="Output directory reset to default: output",
            text_color="blue"
        )
    
    def on_zip_toggle(self):
        """Handle ZIP checkbox toggle to show/hide ZIP filename options"""
        if self.create_zip.get():
            self.zip_name_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=(5, 10))
            self.cleanup_checkbox.configure(state="normal")
            self.output_status.configure(text="ZIP file will be created from generated files")
        else:
            self.zip_name_frame.grid_remove()
            self.cleanup_files.set(False)  # Can't cleanup if no ZIP
            self.cleanup_checkbox.configure(state="disabled")
            self.output_status.configure(text="Files will be saved individually (no ZIP)")
    
    def generate_auto_zip_name(self):
        """Generate automatic ZIP filename based on current parameters"""
        try:
            mode = self.operation_mode.get()
            format_type = self.format.get()
            
            if mode == "csv":
                # For CSV mode, use a generic name
                auto_name = f"qr_codes_csv.{format_type}.zip"
            else:
                # For single/batch mode, use parameters
                uses = self.valid_uses.get() or "15"
                volume = self.volume.get() or "500"
                count = self.count.get() or 1
                auto_name = f"QR-{uses}-{volume}-{count}-{format_type}.zip"
            
            self.zip_filename.set(auto_name)
            self.output_status.configure(
                text=f"✅ Auto-generated ZIP name: {auto_name}",
                text_color="green"
            )
        except Exception as e:
            self.output_status.configure(
                text=f"❌ Error generating ZIP name: {e}",
                text_color="red"
            )
    
    def show_output_section(self, show=True):
        """Show or hide the output configuration section"""
        if show:
            self.output_frame.grid()
            # Update auto ZIP name when section becomes visible
            if not self.zip_filename.get():
                self.generate_auto_zip_name()
        else:
            self.output_frame.grid_remove()
    
    def init_default_values(self):
        """Initialize default values for the form"""
        # Set default operation mode
        self.operation_mode.set("manual")
        
        # Set default preset selection
        self.selected_preset.set("Select preset...")
        
        # Initialize count entry with default value
        self.count_entry.delete(0, 'end')
        self.count_entry.insert(0, "1")
        
        # Disable Generate button initially (will be enabled by validation if form is complete)
        if hasattr(self, 'generate_button'):
            self.generate_button.configure(state="disabled")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_mode = ctk.get_appearance_mode().lower()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
    def generate_qr_codes(self):
        """Main action - generate QR codes with complete workflow integration"""
        try:
            # Update status
            self.status_label.configure(text="Validating inputs...", text_color="orange")
            self.root.update()
            
            # Get current mode
            mode = self.operation_mode.get()
            
            # Validate inputs based on mode
            if mode == "csv":
                if not self.csv_file_path.get():
                    self.status_label.configure(text="Error: Please select a CSV file", text_color="red")
                    return
                if not os.path.exists(self.csv_file_path.get()):
                    self.status_label.configure(text="Error: CSV file not found", text_color="red")
                    return
            else:
                # Validate required parameters for manual mode
                validation_result = self.validate_parameters()
                if not validation_result[0]:
                    self.status_label.configure(text=f"Error: {validation_result[1]}", text_color="red")
                    return
            
            # Update status
            self.status_label.configure(text="Preparing generation...", text_color="orange")
            self.root.update()
            
            # Execute generation based on mode
            if mode == "csv":
                self.execute_csv_generation()
            elif mode == "manual":
                self.execute_manual_generation()
                
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
    
    def validate_parameters(self):
        """Validate all input parameters"""
        try:
            # Validate integer inputs
            valid_uses = validate_integer_input(self.valid_uses.get(), "Valid Uses", 1)
            volume = validate_integer_input(self.volume.get(), "Volume", 1)
            count = validate_integer_input(self.count.get(), "Count", 1)
            
            # Validate date format
            validate_date_format(self.end_date.get())
            
            # Validate color format
            validate_color_format(self.color.get())
            
            # Validate format
            validate_format(self.format.get())
            
            # Validate QR parameters
            if self.qr_version.get():
                validate_qr_version(self.qr_version.get())
            validate_error_correction(self.error_correction.get())
            validate_integer_input(self.box_size.get(), "Box Size", 1, 50)
            validate_integer_input(self.border.get(), "Border", 0, 20)
            
            # Validate format-specific parameters
            if self.format.get() == "png":
                validate_png_quality(self.png_quality.get())
            elif self.format.get() == "svg":
                validate_svg_precision(self.svg_precision.get())
            
            # Validate output directory
            output_dir = self.output_directory.get()
            if not output_dir:
                return False, "Please select an output directory"
            
            return True, "All parameters valid"
            
        except ValueError as e:
            return False, str(e)
    
    def execute_csv_generation(self):
        """Execute CSV-based generation"""
        csv_file = self.csv_file_path.get()
        
        # Load and detect CSV format
        self.status_label.configure(text="Loading CSV file...", text_color="orange")
        self.root.update()
        
        try:
            # Read CSV with auto-delimiter detection
            import csv
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                # Read CSV data
                reader = csv.reader(file, delimiter=delimiter)
                csv_data = list(reader)
                
            if not csv_data:
                self.status_label.configure(text="Error: CSV file is empty", text_color="red")
                return
            
            # Update status
            self.status_label.configure(text=f"Generating {len(csv_data)} QR codes...", text_color="orange")
            self.root.update()
            
            # Call backend function
            result_folder = create_qr_codes(
                valid_uses=self.valid_uses.get(),
                volume=self.volume.get(),
                end_date=self.end_date.get(),
                color=self.color.get(),
                output_folder=self.output_directory.get(),
                format=self.format.get(),
                count=1,
                csv_data=csv_data,
                input_column=self.csv_column.get(),  # Use selected column from preview table
                security_code=self.security_code.get(),
                suffix_code=self.suffix_code.get(),
                qr_version=int(self.qr_version.get()) if self.qr_version.get() else None,
                error_correction=self.error_correction.get(),
                box_size=int(self.box_size.get()),
                border=int(self.border.get()),
                filename_prefix=self.filename_prefix.get(),
                filename_suffix=self.filename_suffix.get(),
                use_payload_as_filename=self.use_payload_filename.get(),
                png_quality=int(self.png_quality.get()) if self.format.get() == "png" else 85,
                svg_precision=int(self.svg_precision.get()) if self.format.get() == "svg" else 2
            )
            
            # Handle ZIP creation if requested
            if self.create_zip.get():
                self.create_zip_file(result_folder)
            
            # Handle cleanup if requested
            if self.cleanup_temp.get():
                self.cleanup_temp_files(result_folder)
            
            self.status_label.configure(text=f"✅ Generated {len(csv_data)} QR codes successfully!", text_color="green")
            
            # Display results (Task 32)
            self.display_generation_results(result_folder, len(csv_data))
            
        except Exception as e:
            self.status_label.configure(text=f"Error processing CSV: {str(e)}", text_color="red")
    
    def execute_manual_generation(self):
        """Execute manual QR code generation (single or batch based on count)"""
        try:
            count = int(self.count.get())
            
            # Dynamic status message based on count
            if count == 1:
                self.status_label.configure(text="Generating QR code...", text_color="orange")
            else:
                self.status_label.configure(text=f"Generating {count} QR codes...", text_color="orange")
            self.root.update()
            
            # Call backend function
            result_folder = create_qr_codes(
                valid_uses=self.valid_uses.get(),
                volume=self.volume.get(),
                end_date=self.end_date.get(),
                color=self.color.get(),
                output_folder=self.output_directory.get(),
                format=self.format.get(),
                count=count,
                csv_data=None,
                security_code=self.security_code.get(),
                suffix_code=self.suffix_code.get(),
                qr_version=int(self.qr_version.get()) if self.qr_version.get() else None,
                error_correction=self.error_correction.get(),
                box_size=int(self.box_size.get()),
                border=int(self.border.get()),
                filename_prefix=self.filename_prefix.get(),
                filename_suffix=self.filename_suffix.get(),
                use_payload_as_filename=self.use_payload_filename.get(),
                png_quality=int(self.png_quality.get()) if self.format.get() == "png" else 85,
                svg_precision=int(self.svg_precision.get()) if self.format.get() == "svg" else 2
            )
            
            # Handle ZIP creation if requested
            if self.create_zip.get():
                self.create_zip_file(result_folder)
            
            # Handle cleanup if requested
            if self.cleanup_temp.get():
                self.cleanup_temp_files(result_folder)
            
            # Dynamic success message based on count
            if count == 1:
                self.status_label.configure(text="✅ Generated QR code successfully!", text_color="green")
            else:
                self.status_label.configure(text=f"✅ Generated {count} QR codes successfully!", text_color="green")
            
            # Display results (Task 32)
            self.display_generation_results(result_folder, count)
            
        except Exception as e:
            self.status_label.configure(text=f"Error generating QR codes: {str(e)}", text_color="red")
    
    def create_zip_file(self, folder_path):
        """Create ZIP file from generated QR codes"""
        try:
            import zipfile
            import datetime
            
            # Create ZIP filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"qr_codes_{timestamp}.zip"
            zip_path = os.path.join(os.path.dirname(folder_path), zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arc_path)
            
            self.status_label.configure(text=f"✅ ZIP created: {zip_filename}", text_color="green")
            
        except Exception as e:
            self.status_label.configure(text=f"Warning: ZIP creation failed: {str(e)}", text_color="orange")
    
    def cleanup_temp_files(self, folder_path):
        """Clean up temporary files if requested"""
        try:
            import shutil
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                
        except Exception as e:
            self.status_label.configure(text=f"Warning: Cleanup failed: {str(e)}", text_color="orange")
    
    def display_generation_results(self, result_folder, file_count):
        """Display generation results with thumbnails (Task 32)"""
        try:
            # Show results section
            self.results_frame.grid()
            
            # Update summary
            self.results_summary.configure(
                text=f"Generated {file_count} QR code(s) in: {result_folder}",
                text_color="green"
            )
            
            # Clear existing thumbnails
            for widget in self.thumbnails_frame.winfo_children():
                widget.destroy()
            
            # Load thumbnails for PNG files only (SVG thumbnails are more complex)
            png_files = []
            if os.path.exists(result_folder):
                for file in os.listdir(result_folder):
                    if file.lower().endswith('.png'):
                        png_files.append(os.path.join(result_folder, file))
            
            # Display thumbnails (limit to first 10 for performance)
            for i, file_path in enumerate(png_files[:10]):
                self.create_thumbnail(file_path, i)
            
            # Enable buttons
            self.open_folder_btn.configure(state="normal")
            self.clear_results_btn.configure(state="normal")
            
            # Store result folder for opening
            self.last_result_folder = result_folder
            
        except Exception as e:
            self.results_summary.configure(
                text=f"Error displaying results: {str(e)}",
                text_color="red"
            )
    
    def create_thumbnail(self, file_path, index):
        """Create a thumbnail widget for a QR code file (Task 32)"""
        try:
            from PIL import Image, ImageTk
            
            # Create thumbnail frame
            thumb_frame = ctk.CTkFrame(self.thumbnails_frame, width=120, height=140)
            thumb_frame.grid(row=0, column=index, padx=5, pady=5)
            thumb_frame.grid_propagate(False)
            
            # Load and resize image
            image = Image.open(file_path)
            image.thumbnail((80, 80), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Image label
            image_label = tk.Label(
                thumb_frame, 
                image=photo,
                bg=thumb_frame.cget("fg_color")[1]
            )
            image_label.image = photo  # Keep reference
            image_label.pack(pady=(10, 5))
            
            # Filename label
            filename = os.path.basename(file_path)
            if len(filename) > 15:
                filename = filename[:12] + "..."
            
            name_label = ctk.CTkLabel(
                thumb_frame,
                text=filename,
                font=ctk.CTkFont(size=10)
            )
            name_label.pack(pady=(0, 5))
            
            # Click to open file
            def open_file():
                try:
                    import subprocess
                    import platform
                    
                    if platform.system() == "Darwin":  # macOS
                        subprocess.call(["open", file_path])
                    elif platform.system() == "Windows":
                        os.startfile(file_path)
                    else:  # Linux
                        subprocess.call(["xdg-open", file_path])
                except Exception:
                    pass
            
            image_label.bind("<Button-1>", lambda e: open_file())
            thumb_frame.bind("<Button-1>", lambda e: open_file())
            
        except ImportError:
            # Fallback if PIL is not available
            thumb_frame = ctk.CTkFrame(self.thumbnails_frame, width=120, height=140)
            thumb_frame.grid(row=0, column=index, padx=5, pady=5)
            
            ctk.CTkLabel(
                thumb_frame,
                text="📄\nQR Code",
                font=ctk.CTkFont(size=12)
            ).pack(expand=True)
            
        except Exception as e:
            # Error creating thumbnail
            thumb_frame = ctk.CTkFrame(self.thumbnails_frame, width=120, height=140)
            thumb_frame.grid(row=0, column=index, padx=5, pady=5)
            
            ctk.CTkLabel(
                thumb_frame,
                text="❌\nError",
                font=ctk.CTkFont(size=12),
                text_color="red"
            ).pack(expand=True)
    
    def open_output_folder(self):
        """Open the output folder in file manager (Task 32)"""
        try:
            if hasattr(self, 'last_result_folder') and os.path.exists(self.last_result_folder):
                import subprocess
                import platform
                
                if platform.system() == "Darwin":  # macOS
                    subprocess.call(["open", self.last_result_folder])
                elif platform.system() == "Windows":
                    os.startfile(self.last_result_folder)
                else:  # Linux
                    subprocess.call(["xdg-open", self.last_result_folder])
            else:
                self.results_summary.configure(
                    text="Output folder no longer exists",
                    text_color="orange"
                )
        except Exception as e:
            self.results_summary.configure(
                text=f"Error opening folder: {str(e)}",
                text_color="red"
            )
    
    def clear_results(self):
        """Clear the results display (Task 32)"""
        try:
            # Clear thumbnails
            for widget in self.thumbnails_frame.winfo_children():
                widget.destroy()
            
            # Reset labels
            self.results_summary.configure(
                text="No QR codes generated yet",
                text_color="gray"
            )
            
            # Disable buttons
            self.open_folder_btn.configure(state="disabled")
            self.clear_results_btn.configure(state="disabled")
            
            # Hide results section
            self.results_frame.grid_remove()
            
        except Exception as e:
            self.results_summary.configure(
                text=f"Error clearing results: {str(e)}",
                text_color="red"
            )
    
    def new_session(self):
        """Start a new session by clearing all data (Task 33)"""
        try:
            self.clear_form()
            self.clear_results()
            self.status_label.configure(text="New session started", text_color="blue")
        except Exception as e:
            self.status_label.configure(text=f"Error starting new session: {str(e)}", text_color="red")
    
    def clear_form(self):
        """Clear all form fields (Task 33)"""
        try:
            # Reset to default values
            self.operation_mode.set("manual")
            self.valid_uses.set("15")
            self.volume.set("500")
            self.end_date.set("26.12.31")
            self.color.set("#000000")
            self.security_code.set("SECD")
            self.suffix_code.set("23FF45EE")
            self.count.set(1)
            self.format.set("png")
            self.png_quality.set(85)
            self.svg_precision.set(2)
            self.qr_version.set("auto")
            self.error_correction.set("L")
            self.box_size.set(10)
            self.border.set(4)
            self.filename_prefix.set("")
            self.filename_suffix.set("")
            self.use_payload_filename.set(True)
            self.output_directory.set("output")
            self.create_zip.set(True)
            self.cleanup_temp.set(False)
            self.csv_file_path.set("")
            self.selected_preset.set("Select preset...")
            
            # Update UI
            self.on_mode_change()
            self.status_label.configure(text="Form cleared", text_color="blue")
            # Trigger validation after clearing form
            self.validate_form()
        except Exception as e:
            self.status_label.configure(text=f"Error clearing form: {str(e)}", text_color="red")
    
    def load_preset_dialog(self):
        """Open dialog to load a preset (Task 33)"""
        try:
            from tkinter import simpledialog, messagebox
            available_presets = list_presets()
            
            if not available_presets:
                messagebox.showinfo("No Presets", "No presets available to load.")
                return
            
            preset_name = simpledialog.askstring(
                "Load Preset", 
                f"Available presets: {', '.join(available_presets)}\\n\\nEnter preset name to load:"
            )
            
            if preset_name:
                success, result = load_preset(preset_name)
                if success:
                    self.load_preset_values(result)
                    self.status_label.configure(text=f"Loaded preset: {preset_name}", text_color="green")
                else:
                    messagebox.showerror("Error", result)
        except Exception as e:
            self.status_label.configure(text=f"Error loading preset: {str(e)}", text_color="red")
    
    def save_preset_dialog(self):
        """Open dialog to save current settings as preset (Task 33)"""
        try:
            from tkinter import simpledialog, messagebox
            
            preset_name = simpledialog.askstring("Save Preset", "Enter name for this preset:")
            
            if preset_name:
                # Get current settings
                preset_data = {
                    "valid_uses": self.valid_uses.get(),
                    "volume": self.volume.get(),
                    "end_date": self.end_date.get(),
                    "color": self.color.get(),
                    "format": self.format.get(),
                    "security_code": self.security_code.get(),
                    "suffix_code": self.suffix_code.get(),
                    "qr_version": self.qr_version.get(),
                    "error_correction": self.error_correction.get(),
                    "box_size": self.box_size.get(),
                    "border": self.border.get(),
                    "filename_prefix": self.filename_prefix.get(),
                    "filename_suffix": self.filename_suffix.get(),
                    "use_payload_as_filename": self.use_payload_filename.get(),
                    "png_quality": self.png_quality.get(),
                    "svg_precision": self.svg_precision.get()
                }
                
                success, result = save_preset(preset_name, preset_data)
                if success:
                    self.refresh_preset_dropdown()
                    self.status_label.configure(text=f"Saved preset: {preset_name}", text_color="green")
                else:
                    messagebox.showerror("Error", result)
        except Exception as e:
            self.status_label.configure(text=f"Error saving preset: {str(e)}", text_color="red")
    
    def show_about(self):
        """Show about dialog (Task 33)"""
        try:
            from tkinter import messagebox
            messagebox.showinfo(
                "About QR Generator",
                "QR Code Generator v2.0\\n\\n"
                "Modern GUI for generating QR codes with customizable parameters.\\n\\n"
                "Features:\\n"
                "• Manual and CSV import modes\\n"
                "• PNG and SVG output formats\\n"
                "• Advanced QR code parameters\\n"
                "• Preset management\\n"
                "• Results viewer with thumbnails\\n\\n"
                "Keyboard Shortcuts:\\n"
                "Ctrl+N: New Session\\n"
                "Ctrl+O: Open CSV\\n"
                "Ctrl+G: Generate QR Codes\\n"
                "Ctrl+T: Toggle Theme\\n"
                "F1: About"
            )
        except Exception as e:
            self.status_label.configure(text=f"Error showing about: {str(e)}", text_color="red")
    
    def get_config_path(self):
        """Get path for configuration file (Task 34)"""
        try:
            import os
            config_dir = os.path.expanduser("~/.qr_generator")
            os.makedirs(config_dir, exist_ok=True)
            return os.path.join(config_dir, "config.json")
        except Exception:
            return "qr_generator_config.json"  # Fallback to current directory
    
    def save_configuration(self):
        """Save current configuration to file (Task 34)"""
        try:
            import json
            
            config = {
                "window": {
                    "geometry": self.root.geometry(),
                    "theme": ctk.get_appearance_mode().lower()
                },
                "last_settings": {
                    "operation_mode": self.operation_mode.get(),
                    "valid_uses": self.valid_uses.get(),
                    "volume": self.volume.get(),
                    "end_date": self.end_date.get(),
                    "color": self.color.get(),
                    "security_code": self.security_code.get(),
                    "suffix_code": self.suffix_code.get(),
                    "count": self.count.get(),
                    "format": self.format.get(),
                    "png_quality": self.png_quality.get(),
                    "svg_precision": self.svg_precision.get(),
                    "qr_version": self.qr_version.get(),
                    "error_correction": self.error_correction.get(),
                    "box_size": self.box_size.get(),
                    "border": self.border.get(),
                    "filename_prefix": self.filename_prefix.get(),
                    "filename_suffix": self.filename_suffix.get(),
                    "use_payload_filename": self.use_payload_filename.get(),
                    "output_directory": self.output_directory.get(),
                    "create_zip": self.create_zip.get(),
                    "cleanup_temp": self.cleanup_temp.get()
                },
                "ui_preferences": {
                    "last_csv_path": getattr(self, 'last_csv_path', ''),
                    "selected_preset": self.selected_preset.get()
                }
            }
            
            with open(self.get_config_path(), 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save configuration: {e}")
    
    def load_configuration(self):
        """Load saved configuration from file (Task 34)"""
        try:
            import json
            
            config_path = self.get_config_path()
            if not os.path.exists(config_path):
                return
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Restore window settings
            if "window" in config:
                window_config = config["window"]
                
                # Restore geometry
                if "geometry" in window_config:
                    try:
                        self.root.geometry(window_config["geometry"])
                    except Exception:
                        pass  # Invalid geometry, use default
                
                # Restore theme
                if "theme" in window_config:
                    try:
                        ctk.set_appearance_mode(window_config["theme"])
                    except Exception:
                        pass  # Invalid theme, use default
            
            # Restore last settings
            if "last_settings" in config:
                settings = config["last_settings"]
                
                # Restore each setting if it exists
                for key, value in settings.items():
                    if hasattr(self, key):
                        try:
                            getattr(self, key).set(value)
                        except Exception:
                            pass  # Invalid value, keep default
            
            # Restore UI preferences
            if "ui_preferences" in config:
                prefs = config["ui_preferences"]
                
                if "last_csv_path" in prefs:
                    self.last_csv_path = prefs["last_csv_path"]
                
                if "selected_preset" in prefs:
                    try:
                        self.selected_preset.set(prefs["selected_preset"])
                    except Exception:
                        pass
            
            # Update UI after loading settings
            self.on_mode_change()
            
        except Exception as e:
            print(f"Failed to load configuration: {e}")
    
    def on_closing(self):
        """Handle application closing (Task 34)"""
        try:
            # Save configuration before closing
            self.save_configuration()
            
            # Close the application
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during application closing: {e}")
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        # Bind window closing event (Task 34)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.root.mainloop()
    
    def setup_form_validation(self):
        """Setup form validation to enable/disable Generate button"""
        try:
            # Bind validation to all form fields that affect generation
            validation_vars = [
                self.operation_mode, self.valid_uses, self.volume, self.end_date,
                self.color, self.security_code, self.suffix_code, self.count,
                self.format, self.qr_version, self.error_correction, self.box_size,
                self.border, self.png_quality, self.svg_precision, self.output_directory,
                self.csv_file_path
            ]
            
            # Bind validation to StringVar and IntVar changes
            for var in validation_vars:
                if hasattr(var, 'trace_add'):
                    var.trace_add('write', self.validate_form)
                else:  # Fallback for older tkinter versions
                    var.trace('w', self.validate_form)
            
            # Initial validation
            self.validate_form()
            
        except Exception as e:
            print(f"Form validation setup failed: {e}")
    
    def validate_form(self, *args):
        """Validate form and enable/disable Generate button"""
        try:
            is_valid = True
            error_message = ""
            
            mode = self.operation_mode.get()
            
            if mode == "csv":
                # CSV mode validation
                csv_path = self.csv_file_path.get().strip()
                if not csv_path:
                    is_valid = False
                    error_message = "Please select a CSV file"
                elif not os.path.exists(csv_path):
                    is_valid = False
                    error_message = "Selected CSV file does not exist"
            
            elif mode == "manual":
                # Manual mode validation
                required_fields = {
                    "Valid Uses": self.valid_uses.get().strip(),
                    "Volume": self.volume.get().strip(), 
                    "End Date": self.end_date.get().strip(),
                    "Color": self.color.get().strip(),
                    "Security Code": self.security_code.get().strip(),
                    "Suffix Code": self.suffix_code.get().strip()
                }
                
                # Check required fields are not empty
                for field_name, value in required_fields.items():
                    if not value:
                        is_valid = False
                        error_message = f"{field_name} is required"
                        break
                
                # Validate numeric fields
                if is_valid:
                    try:
                        valid_uses = int(self.valid_uses.get())
                        if valid_uses < 1:
                            is_valid = False
                            error_message = "Valid Uses must be at least 1"
                    except ValueError:
                        is_valid = False
                        error_message = "Valid Uses must be a number"
                
                if is_valid:
                    try:
                        volume = int(self.volume.get())
                        if volume < 1:
                            is_valid = False
                            error_message = "Volume must be at least 1"
                    except ValueError:
                        is_valid = False
                        error_message = "Volume must be a number"
                
                if is_valid:
                    try:
                        count = int(self.count.get())
                        if count < 1:
                            is_valid = False
                            error_message = "Count must be at least 1"
                    except ValueError:
                        is_valid = False
                        error_message = "Count must be a number"
                
                # Validate date format (basic check)
                if is_valid:
                    date_str = self.end_date.get().strip()
                    if not date_str or len(date_str) < 6:
                        is_valid = False
                        error_message = "End Date must be in format DD.MM.YY"
                
                # Validate color format
                if is_valid:
                    color = self.color.get().strip()
                    if not color.startswith('#') or len(color) != 7:
                        is_valid = False
                        error_message = "Color must be in #RRGGBB format"
            
            # Common validations for both modes
            if is_valid:
                output_dir = self.output_directory.get().strip()
                if not output_dir:
                    is_valid = False
                    error_message = "Output directory is required"
            
            # Update Generate button state
            if hasattr(self, 'generate_button'):
                if is_valid:
                    self.generate_button.configure(state="normal")
                    if hasattr(self, 'status_label'):
                        self.status_label.configure(text="Ready to generate QR codes", text_color="gray")
                else:
                    self.generate_button.configure(state="disabled")
                    if hasattr(self, 'status_label'):
                        self.status_label.configure(text=f"Form incomplete: {error_message}", text_color="orange")
            
        except Exception as e:
            # On validation error, disable button
            if hasattr(self, 'generate_button'):
                self.generate_button.configure(state="disabled")
            print(f"Form validation error: {e}")


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
