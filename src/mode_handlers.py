"""
Mode Handler Pattern for QR Generator Application

This module provides specialized handlers for different generation modes:
- ManualModeHandler: Handles manual parameter input mode
- CSVModeHandler: Handles CSV batch generation mode

Each handler encapsulates mode-specific logic including validation,
UI section visibility, and generation execution.
"""

import os
import tkinter as tk
from abc import ABC, abstractmethod
from src.file_utils import detect_delimiter, zip_output_files, clean_output_folder
from src.qr_core import create_qr_codes
import csv


class ModeHandler(ABC):
    """Abstract base class for mode handlers"""
    
    def __init__(self, gui_app):
        self.gui_app = gui_app
    
    @abstractmethod
    def validate_inputs(self):
        """Validate inputs specific to this mode"""
        pass
    
    @abstractmethod
    def configure_ui_sections(self):
        """Configure UI section visibility for this mode"""
        pass
    
    @abstractmethod
    def execute_generation(self):
        """Execute QR code generation for this mode"""
        pass
    
    @abstractmethod
    def get_auto_filename(self, format_type):
        """Generate automatic filename for this mode"""
        pass


class ManualModeHandler(ModeHandler):
    """Handler for manual parameter input mode"""
    
    def validate_inputs(self):
        """Validate manual mode inputs"""
        # Manual mode validation
        required_fields = {
            "valid_uses": self.gui_app.valid_uses.get().strip(),
            "volume": self.gui_app.volume.get().strip(),
            "end_date": self.gui_app.end_date.get().strip(),
            "color": self.gui_app.color.get().strip(),
        }
        
        # Check for empty required fields
        empty_fields = [field for field, value in required_fields.items() if not value]
        if empty_fields:
            return False, f"Required fields are empty: {', '.join(empty_fields)}"
        
        # Validate count
        try:
            count = int(self.gui_app.count.get())
            if count <= 0:
                return False, "Count must be a positive integer"
        except ValueError:
            return False, "Count must be a valid number"
        
        return True, ""
    
    def configure_ui_sections(self):
        """Configure UI sections for manual mode"""
        self.gui_app.show_csv_section(False)
        self.gui_app.show_parameter_section(True)
        self.gui_app.show_advanced_section(True)
        self.gui_app.show_output_section(True)
    
    def execute_generation(self):
        """Execute manual QR code generation"""
        try:
            count = int(self.gui_app.count.get())
            
            # Start generation progress
            self.gui_app.generation_progress.start_generation(count, "manual")
            
            # Get parameters
            params = self._collect_parameters()
            
            # Generate QR codes
            result_folder = create_qr_codes(**params, count=count, csv_data=None)
            
            # Create ZIP file and cleanup
            zip_path = zip_output_files(result_folder, self._generate_zip_filename(format_type, count), format_type)
            clean_output_folder(result_folder)
            
            # Update UI with results
            self.gui_app.last_zip_path = zip_path
            self.gui_app.generation_progress.complete_generation(count, zip_path)
            
            # Display results
            self.gui_app.results_viewer.display_generation_results(zip_path, count)
            
        except Exception as e:
            self.gui_app.progress.handle_error(e, "QR Generation")
    
    def get_auto_filename(self, format_type):
        """Generate automatic filename for manual mode"""
        try:
            count = int(self.gui_app.count.get())
            if count == 1:
                return f"qr_code.{format_type}.zip"
            else:
                return f"qr_codes_{count}.{format_type}.zip"
        except (ValueError, AttributeError):
            return f"qr_codes.{format_type}.zip"
    
    def _generate_zip_filename(self, format_type, count):
        """Generate ZIP filename for output"""
        if count == 1:
            return f"qr_code.{format_type}"
        else:
            return f"qr_codes_{count}.{format_type}"
    
    def _collect_parameters(self):
        """Collect all parameters for QR generation"""
        return {
            "valid_uses": self.gui_app.valid_uses.get(),
            "volume": self.gui_app.volume.get(),
            "end_date": self.gui_app.end_date.get(),
            "color": self.gui_app.color.get(),
            "output_folder": self.gui_app.output_directory.get(),
            "format": self.gui_app.format.get(),
            "security_code": self.gui_app.security_code.get(),
            "suffix_code": self.gui_app.suffix_code.get(),
            "qr_version": int(self.gui_app.qr_version.get()) if self.gui_app.qr_version.get() and self.gui_app.qr_version.get() != "auto" else None,
            "error_correction": self.gui_app.error_correction.get(),
            "border": int(self.gui_app.border.get()),
            "box_size": int(self.gui_app.box_size.get()),
            "filename_prefix": getattr(self.gui_app, 'filename_prefix', tk.StringVar()).get(),
            "filename_suffix": getattr(self.gui_app, 'filename_suffix', tk.StringVar()).get(),
            "use_payload_as_filename": getattr(self.gui_app, 'use_payload_filename', tk.BooleanVar()).get(),
            "png_quality": int(self.gui_app.png_quality.get()) if self.gui_app.format.get() == "png" else 85,
            "svg_precision": int(getattr(self.gui_app, 'svg_precision', tk.StringVar(value="2")).get()) if self.gui_app.format.get() == "svg" else 2
        }


class CSVModeHandler(ModeHandler):
    """Handler for CSV batch generation mode"""
    
    def validate_inputs(self):
        """Validate CSV mode inputs"""
        csv_path = self.gui_app.csv_file_path.get().strip()
        if not csv_path:
            return False, "Please select a CSV file"
        
        if not os.path.exists(csv_path):
            return False, "Selected CSV file does not exist"
        
        return True, ""
    
    def configure_ui_sections(self):
        """Configure UI sections for CSV mode"""
        self.gui_app.show_csv_section(True)
        self.gui_app.show_parameter_section(False)
        self.gui_app.show_advanced_section(True)
        self.gui_app.show_output_section(True)
    
    def execute_generation(self):
        """Execute CSV-based generation"""
        csv_file = self.gui_app.csv_file_path.get()
        
        # Load and detect CSV format
        self.gui_app.generation_progress.update_csv_loading()
        
        try:
            # Detect delimiter and load CSV
            delimiter = detect_delimiter(csv_file)
            
            # Read CSV data
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                csv_data = list(reader)
            
            if not csv_data:
                raise ValueError("CSV file is empty")
            
            # Get column index for QR data
            column_index = int(self.gui_app.csv_column.get())
            
            # Validate column index
            headers = csv_data[0] if csv_data else []
            if column_index >= len(headers):
                raise ValueError(f"Column index {column_index} is out of range. CSV has {len(headers)} columns.")
            
            # Extract QR data from specified column (skip header if present)
            qr_data_list = [row[column_index] for row in csv_data[1:] if len(row) > column_index]
            
            if not qr_data_list:
                raise ValueError("No valid data found in the specified column")
            
            # Update status
            count = len(qr_data_list)
            self.gui_app.generation_progress.start_generation(count, "csv")
            
            # Get parameters (excluding individual QR data parameters)
            params = self._collect_csv_parameters()
            
            # Generate QR codes from CSV data
            result_folder = create_qr_codes(**params, count=1, csv_data=csv_data, input_column=column_index)
            
            # Create ZIP file and cleanup
            format_type = params["format"]
            zip_path = zip_output_files(result_folder, f"qr_codes_csv.{format_type}", format_type)
            clean_output_folder(result_folder)
            
            # Update UI with results
            self.gui_app.last_zip_path = zip_path
            self.gui_app.generation_progress.complete_generation(count, zip_path)
            
            # Display results
            self.gui_app.results_viewer.display_generation_results(zip_path, count)
            
        except Exception as e:
            self.gui_app.progress.handle_error(e, "QR Generation")
    
    def get_auto_filename(self, format_type):
        """Generate automatic filename for CSV mode"""
        return f"qr_codes_csv.{format_type}.zip"
    
    def _collect_csv_parameters(self):
        """Collect parameters for CSV-based QR generation"""
        return {
            "valid_uses": "15",  # Default for CSV mode
            "volume": "500",     # Default for CSV mode
            "end_date": "31.12.25",  # Default for CSV mode
            "color": self.gui_app.color.get(),
            "output_folder": self.gui_app.output_directory.get(),
            "format": self.gui_app.format.get(),
            "security_code": self.gui_app.security_code.get(),
            "suffix_code": self.gui_app.suffix_code.get(),
            "qr_version": int(self.gui_app.qr_version.get()) if self.gui_app.qr_version.get() and self.gui_app.qr_version.get() != "auto" else None,
            "error_correction": self.gui_app.error_correction.get(),
            "border": int(self.gui_app.border.get()),
            "box_size": int(self.gui_app.box_size.get()),
            "filename_prefix": getattr(self.gui_app, 'filename_prefix', tk.StringVar()).get(),
            "filename_suffix": getattr(self.gui_app, 'filename_suffix', tk.StringVar()).get(),
            "use_payload_as_filename": getattr(self.gui_app, 'use_payload_filename', tk.BooleanVar()).get(),
            "png_quality": int(self.gui_app.png_quality.get()) if self.gui_app.format.get() == "png" else 85,
            "svg_precision": int(getattr(self.gui_app, 'svg_precision', tk.StringVar(value="2")).get()) if self.gui_app.format.get() == "svg" else 2
        }


class ModeHandlerFactory:
    """Factory for creating mode handlers"""
    
    @staticmethod
    def create_handler(mode, gui_app):
        """Create appropriate handler based on mode"""
        if mode == "manual":
            return ManualModeHandler(gui_app)
        elif mode == "csv":
            return CSVModeHandler(gui_app)
        else:
            raise ValueError(f"Unknown mode: {mode}")