import csv
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
from datetime import datetime
import json

# Import validation functions from separate module
from src.validation import (
    validate_integer_input, validate_date_format, validate_color_format,
    validate_format, validate_qr_version, validate_error_correction,
    validate_png_quality, validate_svg_precision, get_error_correction_level
)

# Import preset management functions from separate module  
from src.preset_manager import (
    get_presets_dir, save_preset, load_preset, list_presets, delete_preset,
    create_manual_mode_preset, create_csv_mode_preset, show_preset_menu
)

# Import QR generation core functions from separate module
from src.qr_core import (
    generate_custom_filename, create_qr_codes, colorize_svg
)

# Import file operations from separate module
from src.file_utils import (
    detect_delimiter, zip_output_files, clean_output_folder
)

# Import GUI configuration, widget factory, and results viewer
from src.gui_config import GUIConfig, WidgetFactory
from src.results_viewer import ResultsViewer
from src.mode_handlers import ModeHandlerFactory
from src.progress_handler import ProgressHandler, ValidationProgressHandler, GenerationProgressHandler, StatusType
from src.form_validator import QRFormValidator
from src.config_manager import QRGeneratorConfig, SettingsManager
from src.menu_manager import DynamicMenuManager






class QRGeneratorGUI:
    """Modern GUI interface for QR Generator using CustomTkinter"""
    
    def __init__(self):
        # Set CustomTkinter appearance mode and color theme
        ctk.set_appearance_mode(GUIConfig.APPEARANCE_MODE)
        ctk.set_default_color_theme(GUIConfig.COLOR_THEME)
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("QR Generator Pro - Professional QR Code Generation Tool")
        self.root.geometry(f"{GUIConfig.WINDOW_WIDTH}x{GUIConfig.WINDOW_HEIGHT}")
        self.root.minsize(GUIConfig.MIN_WIDTH, GUIConfig.MIN_HEIGHT)
        
        # Initialize fonts after root window is created
        GUIConfig.init_fonts()
        
        # Center window on screen
        self.center_window()
        
        # Initialize GUI state variables
        self.operation_mode = tk.StringVar(value="manual")  # manual, csv
        self.selected_preset = tk.StringVar(value="")
        self.csv_file_path = tk.StringVar(value="")
        
        # Parameter form variables
        self.valid_uses = tk.StringVar(value="")  # Start empty - user must fill
        self.volume = tk.StringVar(value="") # Start empty - user must fill
        self.end_date = tk.StringVar(value="") # Start empty - user must fill
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
        self.settings_manager.restore_session()
        
        # Setup form validation
        self.setup_form_validation()
        
        # Ensure button starts disabled (force initial state)
        if hasattr(self, 'generate_button'):
            self.progress.disable_button("generate")
            # Only enable after validation if form is truly complete
            self.root.after(100, self.delayed_validation)
    
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
        
    
    def create_menu_bar(self):
        """Create menu bar using data-driven approach"""
        try:
            # Initialize menu manager
            self.menu_manager = DynamicMenuManager(self.root)
            
            # Create menus from configuration
            self.menubar = self.menu_manager.create_qr_generator_menus(self)
            
        except Exception as e:
            print(f"Menu bar creation failed: {e}")
    
    def create_header_section(self):
        """Create header with title and theme toggle (Task 35 - Branding)"""
        header_frame = ctk.CTkFrame(self.root)
        header_frame.grid(row=0, column=0, sticky=GUIConfig.STICKY_EW, 
                         padx=GUIConfig.CONTENT_PADX, pady=(GUIConfig.CONTENT_PADX, 10))
        header_frame.grid_columnconfigure(2, weight=1)
        
        # App icon (if available)
        try:
            if os.path.exists('icon_32.png'):
                icon_image = tk.PhotoImage(file='icon_32.png')
                icon_label = ctk.CTkLabel(header_frame, image=icon_image, text="")
                icon_label.image = icon_image  # Keep a reference
                icon_label.grid(row=0, column=0, padx=GUIConfig.CONTENT_PADX, 
                               pady=GUIConfig.CONTENT_PADY, sticky=GUIConfig.STICKY_W)
        except Exception:
            pass
        
        # Title with branding
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, padx=GUIConfig.CONTENT_PADX, 
                        pady=GUIConfig.CONTENT_PADY, sticky=GUIConfig.STICKY_W)
        
        main_title = ctk.CTkLabel(
            title_frame,
            text="QR Generator Pro",
            font=GUIConfig.TITLE_FONT
        )
        main_title.grid(row=0, column=0, sticky=GUIConfig.STICKY_W)
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Professional QR Code Generation Tool",
            font=GUIConfig.SMALL_FONT,
            text_color="gray"
        )
        subtitle.grid(row=1, column=0, sticky=GUIConfig.STICKY_W)
        
        # Version info
        version_label = ctk.CTkLabel(
            header_frame,
            text="v2.0",
            font=GUIConfig.TINY_FONT,
            text_color="gray"
        )
        version_label.grid(row=0, column=3, padx=(0, 10), pady=GUIConfig.CONTENT_PADY, 
                          sticky="ne")
        
        # Theme toggle button
        theme_button = ctk.CTkButton(
            header_frame,
            text="🌙/☀️",
            width=50,
            command=self.toggle_theme
        )
        theme_button.grid(row=0, column=4, padx=GUIConfig.CONTENT_PADX, 
                         pady=GUIConfig.CONTENT_PADY, sticky=GUIConfig.STICKY_E)
    
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
    
    def create_results_viewer_section(self):
        """Create generation results viewer with thumbnails (Task 32)"""
        # Initialize the ResultsViewer component
        self.results_viewer = ResultsViewer(self.content_frame, self)
        
        # Initialize progress handlers
        self.progress = ProgressHandler(self.status_label, self.root)
        self.validation_progress = ValidationProgressHandler(self.status_label, self.root)
        self.generation_progress = GenerationProgressHandler(self.status_label, self.root)
        
        # Register buttons for centralized state management
        self.progress.register_button("generate", self.generate_button)
        if hasattr(self, 'cleanup_checkbox'):
            self.progress.register_button("cleanup", self.cleanup_checkbox)
        
        # Initialize form validator
        self.form_validator = QRFormValidator(self)
        
        # Initialize configuration manager
        self.config_manager = QRGeneratorConfig()
        self.config_manager.set_gui_app(self)
        self.settings_manager = SettingsManager(self.config_manager)
        
        # Initialize mode handler for current mode
        self._current_mode_handler = None
    
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
        mode_frame, _ = WidgetFactory.create_section(
            self.content_frame, "Generation Mode:", 0, {1: 1}
        )
        
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
        preset_frame, _ = WidgetFactory.create_section(
            self.content_frame, "Parameter Presets:", 1, {1: 1}
        )
        
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
                # Apply preset values to form fields
                # This functionality can be extended as needed
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
            # Collect current form values
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
        self.csv_frame, _ = WidgetFactory.create_section(
            self.content_frame, "CSV File Selection:", 2, {1: 1}
        )
        
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
            # ttk.Style() can be used here to customize appearance if needed
            
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
            self.progress.show_error(f"Error selecting file: {e}")
    
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
            for _, row in enumerate(rows[:max_rows]):
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
    
    def get_current_mode_handler(self):
        """Get current mode handler, creating if necessary"""
        mode = self.operation_mode.get()
        if self._current_mode_handler is None or not isinstance(self._current_mode_handler, type(ModeHandlerFactory.create_handler(mode, self))):
            self._current_mode_handler = ModeHandlerFactory.create_handler(mode, self)
        return self._current_mode_handler
    
    def on_mode_change(self):
        """Handle operation mode changes to show/hide relevant sections"""
        mode = self.operation_mode.get()
        
        # Create/update mode handler
        self._current_mode_handler = ModeHandlerFactory.create_handler(mode, self)
        
        # Configure UI sections using mode handler
        self._current_mode_handler.configure_ui_sections()
        
        # Set appropriate status messages
        if mode == "csv":
            self.progress.show_info("CSV mode selected - choose a CSV file to import data")
        elif mode == "manual":
            self.progress.show_info("Manual mode selected - enter QR code parameters (set count: 1 for single, multiple for batch)")
            
        # Trigger validation after mode change
        self.validate_form()
    
    def create_parameter_forms_section(self):
        """Create parameter input forms with validation (Task 25)"""
        self.params_frame, _ = WidgetFactory.create_section(
            self.content_frame, "QR Code Parameters:", 3, {1: 1, 3: 1}
        )
        
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
        self.format_frame, _ = WidgetFactory.create_section(
            self.content_frame, "Format & Advanced Options:", 4, {1: 1, 3: 1}
        )
        
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
        self.output_frame, _ = WidgetFactory.create_section(
            self.content_frame, "Output Configuration:", 5, {1: 1}
        )
        
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
            self.progress.enable_button("cleanup")
            self.output_status.configure(text="ZIP file will be created from generated files")
        else:
            self.zip_name_frame.grid_remove()
            self.cleanup_files.set(False)  # Can't cleanup if no ZIP
            self.progress.disable_button("cleanup")
            self.output_status.configure(text="Files will be saved individually (no ZIP)")
    
    def generate_auto_zip_name(self):
        """Generate automatic ZIP filename based on current parameters"""
        try:
            format_type = self.format.get()
            handler = self.get_current_mode_handler()
            auto_name = handler.get_auto_filename(format_type)
            
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
            self.progress.disable_button("generate")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_mode = ctk.get_appearance_mode().lower()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
    def generate_qr_codes(self):
        """Main action - generate QR codes with complete workflow integration"""
        try:
            # Start validation progress
            self.validation_progress.show_validation_in_progress()
            
            # Get current mode handler
            handler = self.get_current_mode_handler()
            
            # Validate inputs using mode handler
            is_valid, error_message = handler.validate_inputs()
            if not is_valid:
                self.progress.show_error(f"Error: {error_message}")
                return
            
            # Start generation progress
            self.progress.start_operation("QR Generation", "Preparing generation...")
            
            # Execute generation using mode handler
            handler.execute_generation()
                
        except Exception as e:
            self.progress.handle_error(e, "QR Generation")
    
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
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, folder_path)
                        zipf.write(file_path, arc_path)
            
            self.progress.show_success(f"✅ ZIP created: {zip_filename}")
            
        except Exception as e:
            self.progress.show_warning(f"Warning: ZIP creation failed: {str(e)}")
    
    def cleanup_temp_files(self, folder_path):
        """Clean up temporary files if requested"""
        try:
            import shutil
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                
        except Exception as e:
            self.progress.show_warning(f"Warning: Cleanup failed: {str(e)}")
    
    
    
    def open_output_folder(self):
        """Open the output folder in file manager (Task 32)"""
        self.results_viewer.open_output_folder()
    
    def clear_results(self):
        """Clear the results display (Task 32)"""
        self.results_viewer.clear_results()
    
    def new_session(self):
        """Start a new session by clearing all data (Task 33)"""
        try:
            self.clear_form()
            self.results_viewer.clear_results()
            self.progress.show_info("New session started")
        except Exception as e:
            self.progress.handle_error(e, "Session reset")
    
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
            self.progress.show_info("Form cleared")
            # Trigger validation after clearing form
            self.validate_form()
        except Exception as e:
            self.progress.handle_error(e, "Form clearing")
    
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
                    self.progress.update_status(f"Loaded preset: {preset_name}", StatusType.SUCCESS)
                else:
                    messagebox.showerror("Error", result)
        except Exception as e:
            self.progress.update_status(f"Error loading preset: {str(e)}", StatusType.ERROR)
    
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
                    self.progress.update_status(f"Saved preset: {preset_name}", StatusType.SUCCESS)
                else:
                    messagebox.showerror("Error", result)
        except Exception as e:
            self.progress.update_status(f"Error saving preset: {str(e)}", StatusType.ERROR)
    
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
            self.progress.update_status(f"Error showing about: {str(e)}", StatusType.ERROR)
    
    def on_closing(self):
        """Handle application closing (Task 34)"""
        try:
            # Save configuration before closing
            self.settings_manager.save_session()
            
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
            # Use rule-based form validation
            is_valid, error_message = self.form_validator.validate_current_form()
            
            # Update Generate button state
            if hasattr(self, 'generate_button'):
                if is_valid:
                    self.progress.enable_button("generate")
                    if hasattr(self, 'validation_progress'):
                        self.validation_progress.show_validation_success()
                else:
                    self.progress.disable_button("generate")
                    if hasattr(self, 'validation_progress'):
                        self.validation_progress.show_validation_error([error_message])
            
        except Exception as e:
            # On validation error, disable button
            if hasattr(self, 'generate_button'):
                self.progress.disable_button("generate")
            print(f"Form validation error: {e}")
    
    def delayed_validation(self):
        """Delayed validation check for startup"""
        try:
            # Only run validation if all default values are actually set
            if (self.valid_uses.get().strip() and 
                self.volume.get().strip() and 
                self.end_date.get().strip() and 
                self.color.get().strip() and 
                self.security_code.get().strip() and 
                self.suffix_code.get().strip() and
                self.output_directory.get().strip()):
                self.validate_form()
            else:
                # Keep button disabled if any required field is empty
                if hasattr(self, 'generate_button'):
                    self.progress.disable_button("generate")
                if hasattr(self, 'status_label'):
                    self.progress.update_status("Form incomplete: Fill all required fields", StatusType.WARNING)
        except Exception as e:
            if hasattr(self, 'generate_button'):
                self.progress.disable_button("generate")
            print(f"Delayed validation error: {e}")


def main():
    """Main entry point - uses modern GUI interface"""
    try:
        # Create and run the modern GUI
        app = QRGeneratorGUI()
        app.run()
    except Exception as e:
        print(f"Application failed to start: {e}")
        print("Please check your Python environment and dependencies.")
        raise


if __name__ == "__main__":
    main()
