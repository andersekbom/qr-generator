"""
File operations utilities for QR Generator Pro
Handles CSV processing, ZIP operations, and file management
"""

import os
import csv
import zipfile


def detect_delimiter(file_path):
    """Detect the delimiter used in a CSV file"""
    with open(file_path, "r") as infile:
        sample = infile.read(1024)
        return csv.Sniffer().sniff(sample).delimiter


def zip_output_files(output_folder, zip_file_name, format):
    """Create a ZIP file containing all generated files of the specified format"""
    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.endswith(f".{format}"):
                    zipf.write(os.path.join(root, file), arcname=file)


def clean_output_folder(output_folder):
    """Remove all files from the output folder"""
    for root, _, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))