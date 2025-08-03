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

import PIL
from PIL import Image, ImageDraw


def detect_delimiter(file_path):
    with open(file_path, "r") as infile:
        sample = infile.read(1024)
        return csv.Sniffer().sniff(sample).delimiter

def create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count, csv_data=None, input_column=0):
    """
    Create QR codes either from manual parameters or CSV data
    
    Args:
        csv_data: List of CSV rows (None for manual mode)
        input_column: Column index to use from CSV data
        Other parameters: Used for manual mode or as defaults
    """
    os.makedirs(output_folder, exist_ok=True)
    factory = qrcode.image.svg.SvgFillImage if format == 'svg' else None

    if csv_data is not None:
        # CSV mode: generate QR codes from CSV data
        for i, row in enumerate(tqdm(csv_data, desc="Generating QR codes from CSV")):
            if len(row) <= input_column:
                print(f"Warning: Row {i+1} doesn't have column {input_column}, skipping")
                continue
            
            payload = row[input_column]
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
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
            payload = f"M-{valid_uses}-{serial}-{volume}-{end_date}-SECD-23FF45EE"
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
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
            format = simpledialog.askstring("Input", "Image format [png,svg]:", initialvalue="png")
            color = simpledialog.askstring("Input", "Image color [hex or name]:", initialvalue="#000000")
            
            # Read CSV data
            with open(input_file, "r") as infile:
                reader = csv.reader(infile, delimiter=delimiter)
                if skip_first_row:
                    next(reader)
                rows = list(reader)
            
            if not rows:
                messagebox.showerror("Error", "No data found in CSV file.")
                return
                
            zip_output = messagebox.askyesno("Input", "Add output files to a zip file?")
            zip_file_name = None
            if zip_output:
                zip_file_name = simpledialog.askstring("Input", f"Enter zip file name [output_{format}.zip]:", initialvalue=f"output_{format}.zip")
            
            output_folder = "output"
            
            # Generate QR codes from CSV data
            create_qr_codes(None, None, None, color, output_folder, format, None, csv_data=rows, input_column=input_column)
            
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
    valid_uses = simpledialog.askstring("Input", "Enter Valid uses (e.g. 15):")
    if not valid_uses:
        messagebox.showerror("Error", "No valid uses entered. Exiting.")
        return

    volume = simpledialog.askstring("Input", "Enter Volume (e.g. 500):")
    if not volume:
        messagebox.showerror("Error", "No volume entered. Exiting.")
        return

    end_date = simpledialog.askstring("Input", "Enter Valid Until date:", initialvalue="26.12.31")
    if not end_date:
        messagebox.showerror("Error", "No end date entered. Exiting.")
        return

    color = simpledialog.askstring("Input", "Image color [hex or name]:", initialvalue="#000000")
    format = simpledialog.askstring("Input", "Image format [png,svg]:", initialvalue="png")
    count = simpledialog.askinteger("Input", "How many QR codes to generate?", initialvalue=1)
    if not count or count < 1:
        messagebox.showerror("Error", "Invalid count. Exiting.")
        return

    zip_output = messagebox.askyesno("Input", "Add output files to a zip file?")
    zip_file_name = None
    if zip_output:
        zip_file_name = simpledialog.askstring("Input", f"Enter zip file name:", initialvalue=f"QR-{valid_uses}-{volume}-{color}-{count}-{format}.zip")

    output_folder = "output"
    try:
        create_qr_codes(valid_uses, volume, end_date, color, output_folder, format, count)
        #messagebox.showinfo("Success", f"{count} QR codes generated successfully!")

        #if zip_output:
        zip_output_files(output_folder, zip_file_name, format)

        clean_output_folder(output_folder)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    main()
