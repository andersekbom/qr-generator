import qrcode
import qrcode.image.svg
import csv
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import re
from tqdm import tqdm
import xml.etree.ElementTree as ET
from datetime import datetime

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

def get_error_correction_level(level_str):
    """Convert error correction string to qrcode constant"""
    levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    return levels.get(level_str.upper(), qrcode.constants.ERROR_CORRECT_L)

def detect_delimiter(file_path):
    with open(file_path, "r") as infile:
        sample = infile.read(1024)
        return csv.Sniffer().sniff(sample).delimiter

def create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count, csv_data=None, input_column=0, security_code="SECD", suffix_code="23FF45EE", qr_version=None, error_correction="L", box_size=10, border=4):
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

            # Create safe filename from payload
            safe_filename = "".join(c for c in payload if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            if not safe_filename:
                safe_filename = f"qr_code_{i+1}"
            filename = os.path.join(output_folder, f"{safe_filename}.{format}")
            img.save(filename)
            if format == 'svg':
                colorize_svg(filename, color)
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

            filename = os.path.join(output_folder, f"{payload}.{format}")
            img.save(filename)
            if format == 'svg':
                colorize_svg(filename, color)

def zip_output_files(output_folder, zip_file_name, format):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith(f".{format}"):
                    zipf.write(os.path.join(root, file), arcname=file)
    #messagebox.showinfo("Success", f"Output files added to zip file '{zip_file_name}' successfully!")

def colorize_svg(svg_file, color, background_color="#FFFFFF"):
    """
    Colorize SVG using proper XML manipulation with namespace handling.
    
    Args:
        svg_file (str): Path to SVG file
        color (str): Foreground color for QR code modules
        background_color (str): Background color (default white)
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

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Ask user to choose input mode
    input_mode = messagebox.askyesno("Input Mode", "Use CSV file for input?\n\nYes = CSV file input\nNo = Manual parameter input")
    
    if input_mode:
        # CSV mode - get file and process it
        input_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
        if not input_file:
            messagebox.showerror("Error", "No file selected. Exiting.")
            return
        
        # Process CSV file
        try:
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
            
            # Ask for advanced QR code parameters
            advanced_qr = messagebox.askyesno("QR Parameters", "Configure advanced QR code parameters?")
            qr_version, error_correction, box_size, border = None, "L", 10, 4
            
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
            
            # For CSV mode, we don't use the sequential payload format, so we skip security_code and suffix_code
            # Generate QR codes from CSV data
            create_qr_codes(None, None, None, color, output_folder, format, None, csv_data=rows, input_column=input_column, qr_version=qr_version, error_correction=error_correction, box_size=box_size, border=border)
            
            messagebox.showinfo("Success", f"{len(rows)} QR codes generated successfully from CSV!")
            
            if zip_output:
                zip_output_files(output_folder, zip_file_name, format)
            
            clean_output_folder(output_folder)
            return
            
        except FileNotFoundError:
            messagebox.showerror("Error", f"File '{input_file}' not found. Please check the filename and try again.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error processing CSV file: {e}")
            return
    
    # Manual parameter input mode
    # Validate valid_uses
    valid_uses_input = simpledialog.askstring("Input", "Enter Valid uses (e.g. 15):")
    if not valid_uses_input:
        messagebox.showerror("Error", "No valid uses entered. Exiting.")
        return
    
    valid_uses_valid, valid_uses_result = validate_integer_input(valid_uses_input, "Valid uses", 1, 9999)
    if not valid_uses_valid:
        messagebox.showerror("Validation Error", valid_uses_result)
        return
    valid_uses = str(valid_uses_result)

    # Validate volume
    volume_input = simpledialog.askstring("Input", "Enter Volume (e.g. 500):")
    if not volume_input:
        messagebox.showerror("Error", "No volume entered. Exiting.")
        return
    
    volume_valid, volume_result = validate_integer_input(volume_input, "Volume", 1, 99999)
    if not volume_valid:
        messagebox.showerror("Validation Error", volume_result)
        return
    volume = str(volume_result)

    # Validate end_date
    end_date_input = simpledialog.askstring("Input", "Enter Valid Until date:", initialvalue="26.12.31")
    if not end_date_input:
        messagebox.showerror("Error", "No end date entered. Exiting.")
        return
    
    date_valid, date_result = validate_date_format(end_date_input)
    if not date_valid:
        messagebox.showerror("Validation Error", date_result)
        return
    end_date = date_result

    # Validate color
    color_input = simpledialog.askstring("Input", "Image color [hex or name]:", initialvalue="#000000")
    color_valid, color_result = validate_color_format(color_input)
    if not color_valid:
        messagebox.showerror("Validation Error", color_result)
        return
    color = color_result
    
    # Validate format
    format_input = simpledialog.askstring("Input", "Image format [png,svg]:", initialvalue="png")
    format_valid, format_result = validate_format(format_input)
    if not format_valid:
        messagebox.showerror("Validation Error", format_result)
        return
    format = format_result
    
    # Validate count
    count = simpledialog.askinteger("Input", "How many QR codes to generate?", initialvalue=1)
    if not count:
        messagebox.showerror("Error", "No count entered. Exiting.")
        return
    
    count_valid, count_result = validate_integer_input(count, "Count", 1, 10000)
    if not count_valid:
        messagebox.showerror("Validation Error", count_result)
        return
    count = count_result

    # Ask for payload customization options
    security_code = simpledialog.askstring("Input", "Enter security code:", initialvalue="SECD")
    if not security_code:
        messagebox.showerror("Error", "No security code entered. Exiting.")
        return
    
    suffix_code = simpledialog.askstring("Input", "Enter suffix code:", initialvalue="23FF45EE")
    if not suffix_code:
        messagebox.showerror("Error", "No suffix code entered. Exiting.")
        return

    # Ask for advanced QR code parameters
    advanced_qr = messagebox.askyesno("QR Parameters", "Configure advanced QR code parameters?")
    qr_version, error_correction, box_size, border = None, "L", 10, 4
    
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
        zip_file_name = simpledialog.askstring("Input", f"Enter zip file name:", initialvalue=f"QR-{valid_uses}-{volume}-{color}-{count}-{format}.zip")

    try:
        create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count, security_code=security_code, suffix_code=suffix_code, qr_version=qr_version, error_correction=error_correction, box_size=box_size, border=border)
        #messagebox.showinfo("Success", f"{count} QR codes generated successfully!")

        #if zip_output:
        zip_output_files(output_folder, zip_file_name, format)

        clean_output_folder(output_folder)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()
