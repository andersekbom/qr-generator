import qrcode
import qrcode.image.svg
import csv
from tqdm import tqdm
from colorama import Fore, Style
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from qrcode.image.pil import Image, PilImage
from PIL import Image, ImageDraw
import re

def detect_delimiter(file_path):
    with open(file_path, "r") as infile:
        sample = infile.read(1024)
        return csv.Sniffer().sniff(sample).delimiter


def create_qr_codes(rows, output_folder, input_column, format, color):
    os.makedirs(output_folder, exist_ok=True)
    factory = qrcode.image.svg.SvgImage if format == 'svg' else None
    counter = 0

    with tqdm(total=len(rows)) as pbar:
        for row in rows:
            payload = row[input_column]
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color=color, back_color="#FFFFFF", image_factory=factory)
            img.save(os.path.join(output_folder, f"{payload}.{format}"))
            if format == 'svg':
                colorize_svg(os.path.join(output_folder, f"{payload}.{format}"), color)
            counter += 1
            pbar.update(1)

def zip_output_files(output_folder, zip_file_name, format):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith(f".{format}"):
                    zipf.write(os.path.join(root, file), arcname=file)
    messagebox.showinfo("Success", f"Output files added to zip file '{zip_file_name}' successfully!")

def colorize_svg(svg_file, color):
    with open(svg_file, 'r') as file:
        svg_content = file.read()
    colored_svg = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg_content)
    with open(svg_file, 'w') as file:
        file.write(colored_svg)

def clean_output_folder(output_folder):
    for root, _, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    input_file = filedialog.askopenfilename(title="Select Input File", filetypes=[("CSV Files", "*.csv")])
    if not input_file:
        messagebox.showerror("Error", "No file selected. Exiting.")
        return

    detected_delimiter = detect_delimiter(input_file)
    delimiter = simpledialog.askstring("Input", f"Enter separator [{detected_delimiter}]:") or detected_delimiter
    input_column = simpledialog.askinteger("Input", "Enter 0-indexed input column [0]:", initialvalue=0)
    skip_first_row = messagebox.askyesno("Input", "Skip first row?")
    format = simpledialog.askstring("Input", "Image format [png,svg]:", initialvalue="png")
    color = simpledialog.askstring("Input", "Image color [hex or name]:", initialvalue="#000000")

    zip_output = messagebox.askyesno("Input", "Add output files to a zip file?")
    zip_file_name = None
    if zip_output:
        zip_file_name = simpledialog.askstring("Input", f"Enter zip file name [output_{format}.zip]:", initialvalue=f"output_{format}.zip")

    try:
        with open(input_file, "r") as infile:
            reader = csv.reader(infile, delimiter=delimiter)
            if skip_first_row:
                next(reader)

            rows = list(reader)
            output_folder = "output"
            counter = create_qr_codes(rows, output_folder, input_column, format, color)

            messagebox.showinfo("Success", f"{counter} QR codes generated successfully!")

            if zip_output:
                zip_output_files(output_folder, zip_file_name, format)

            clean_output_folder(output_folder)

    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{input_file}' not found. Please check the filename and try again.")


if __name__ == "__main__":
    main()
