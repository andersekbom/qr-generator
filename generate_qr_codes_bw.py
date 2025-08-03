import qrcode
import qrcode.image.svg
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tqdm import tqdm
from colorama import Fore, Style


def create_qr_codes(num_codes, output_folder, format, expiry_date, volume, usage_limit):
    os.makedirs(output_folder, exist_ok=True)
    factory = qrcode.image.svg.SvgImage if format == 'svg' else None

    with tqdm(total=num_codes) as pbar:
        for i in range(num_codes):
            payload = 'M-'+usage_limit+'-'+volume+'-'+str(i+1)+'-' + expiry_date
            payload_str = str(payload)
            img = qrcode.make(payload_str, image_factory=factory)
            img.save(os.path.join(output_folder, f"code_{i + 1}.{format}"))
            pbar.update(1)


def zip_output_files(output_folder, zip_file_name, format):
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith(f".{format}"):
                    zipf.write(os.path.join(root, file), arcname=file)
    messagebox.showinfo("Success", f"Output files added to zip file '{zip_file_name}' successfully!")


def clean_output_folder(output_folder):
    for root, _, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))


def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    num_codes = simpledialog.askinteger("Input", "Enter the number of QR codes to generate:", minvalue=1)
    expiry_date = simpledialog.askstring("Input", "Enter the expiry date (e.g., YYYY-MM-DD):")
    volume = simpledialog.askstring("Input", "Enter the volume (e.g., 100ml):")
    usage_limit = simpledialog.askinteger("Input", "Enter how many times each code can be used:", minvalue=1)
    format = simpledialog.askstring("Input", "Image format [png,svg]:", initialvalue="png")

    zip_file_name = simpledialog.askstring("Input", f"Enter zip file name [output_{format}.zip]:", initialvalue=f"output_{format}.zip")

    try:
        output_folder = "output"
        create_qr_codes(num_codes, output_folder, format, expiry_date, volume, usage_limit)

        messagebox.showinfo("Success", f"{num_codes} QR codes generated successfully!")

        zip_output_files(output_folder, zip_file_name, format)

        clean_output_folder(output_folder)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    main()
