"""
GUI configuration and widget factory methods for QR Generator Pro
Centralizes styling, constants, and common widget creation patterns
"""

import customtkinter as ctk
from tkinter import colorchooser


class GUIConfig:
    """Configuration constants for the GUI"""
    
    # Colors and Theme
    APPEARANCE_MODE = "system"
    COLOR_THEME = "blue"
    
    # Font configurations (initialized after root window is created)
    TITLE_FONT = None
    SECTION_FONT = None
    LABEL_FONT = None
    SMALL_FONT = None
    TINY_FONT = None
    
    @classmethod
    def init_fonts(cls):
        """Initialize fonts after root window is created"""
        if cls.TITLE_FONT is None:
            cls.TITLE_FONT = ctk.CTkFont(size=26, weight="bold")
            cls.SECTION_FONT = ctk.CTkFont(size=16, weight="bold")
            cls.LABEL_FONT = ctk.CTkFont(size=12)
            cls.SMALL_FONT = ctk.CTkFont(size=11)
            cls.TINY_FONT = ctk.CTkFont(size=10)
    
    # Padding and Spacing
    SECTION_PADX = 10
    SECTION_PADY = 10
    CONTENT_PADX = 20
    CONTENT_PADY = 15
    WIDGET_PADX = 15
    WIDGET_PADY = 8
    
    # Widget Dimensions
    BUTTON_WIDTH = 120
    BUTTON_HEIGHT = 40
    ENTRY_WIDTH = 200
    DROPDOWN_WIDTH = 200
    PROGRESS_BAR_WIDTH = 200
    PROGRESS_BAR_HEIGHT = 20
    
    # Window Settings
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 700
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    
    # Grid Settings
    STICKY_EW = "ew"
    STICKY_W = "w"
    STICKY_E = "e"
    STICKY_NSEW = "nsew"


class WidgetFactory:
    """Factory methods for creating commonly used widgets with consistent styling"""
    
    @staticmethod
    def create_section(parent, title, row, column_config=None):
        """Create a standardized section frame with title
        
        Args:
            parent: Parent widget
            title: Section title text
            row: Grid row position
            column_config: Dict with column weights (e.g., {1: 1, 3: 1})
        
        Returns:
            Tuple of (frame, title_label)
        """
        GUIConfig.init_fonts()
        
        # Create main section frame
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky=GUIConfig.STICKY_EW, 
                  padx=GUIConfig.SECTION_PADX, pady=GUIConfig.SECTION_PADY)
        
        # Configure columns
        if column_config:
            for col, weight in column_config.items():
                frame.grid_columnconfigure(col, weight=weight)
        else:
            frame.grid_columnconfigure(1, weight=1)  # Default
        
        # Add section title
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=GUIConfig.SECTION_FONT
        )
        title_label.grid(row=0, column=0, columnspan=4, 
                        padx=GUIConfig.CONTENT_PADX, 
                        pady=(15, 10), 
                        sticky=GUIConfig.STICKY_W)
        
        return frame, title_label
    
    @staticmethod
    def create_section_frame(parent, row):
        """Create a section frame with standard styling (legacy method)"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky=GUIConfig.STICKY_EW, 
                  padx=GUIConfig.SECTION_PADX, pady=GUIConfig.SECTION_PADY)
        frame.grid_columnconfigure(1, weight=1)
        return frame
    
    @staticmethod
    def create_section_title(parent, text, row=0, columnspan=2):
        """Create a section title label with standard styling"""
        GUIConfig.init_fonts()
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=GUIConfig.SECTION_FONT
        )
        label.grid(row=row, column=0, columnspan=columnspan, 
                  padx=GUIConfig.CONTENT_PADX, pady=(GUIConfig.CONTENT_PADY, 10), 
                  sticky=GUIConfig.STICKY_W)
        return label
    
    @staticmethod
    def create_labeled_entry(parent, label_text, textvariable, placeholder="", row=0, trace_callback=None):
        """Create a labeled entry field with standard styling"""
        # Create container frame
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.grid(row=row, column=0, columnspan=2, sticky=GUIConfig.STICKY_EW, 
                        padx=GUIConfig.WIDGET_PADX, pady=5)
        entry_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        GUIConfig.init_fonts()
        label = ctk.CTkLabel(entry_frame, text=label_text, font=GUIConfig.LABEL_FONT)
        label.grid(row=0, column=0, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                  sticky=GUIConfig.STICKY_W)
        
        # Entry
        entry = ctk.CTkEntry(
            entry_frame,
            textvariable=textvariable,
            placeholder_text=placeholder,
            width=GUIConfig.ENTRY_WIDTH
        )
        entry.grid(row=0, column=1, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                  sticky=GUIConfig.STICKY_EW)
        
        # Add trace if provided
        if trace_callback:
            textvariable.trace_add('write', trace_callback)
        
        return entry_frame, label, entry
    
    @staticmethod
    def create_slider_with_label(parent, label_text, variable, from_=0, to=100, row=0, value_label=None):
        """Create a slider with label and value display"""
        # Create container frame
        slider_frame = ctk.CTkFrame(parent)
        slider_frame.grid(row=row, column=0, columnspan=2, sticky=GUIConfig.STICKY_EW, 
                         padx=GUIConfig.WIDGET_PADX, pady=5)
        slider_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        GUIConfig.init_fonts()
        label = ctk.CTkLabel(slider_frame, text=label_text, font=GUIConfig.LABEL_FONT)
        label.grid(row=0, column=0, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                  sticky=GUIConfig.STICKY_W)
        
        # Slider
        slider = ctk.CTkSlider(
            slider_frame,
            variable=variable,
            from_=from_,
            to=to
        )
        slider.grid(row=0, column=1, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                   sticky=GUIConfig.STICKY_EW)
        
        # Value label
        if value_label is not None:
            value_label.grid(row=0, column=2, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                           sticky=GUIConfig.STICKY_W)
        
        return slider_frame, label, slider
    
    @staticmethod
    def create_combo_box(parent, label_text, variable, values, row=0, command=None):
        """Create a labeled combo box with standard styling"""
        # Create container frame
        combo_frame = ctk.CTkFrame(parent)
        combo_frame.grid(row=row, column=0, columnspan=2, sticky=GUIConfig.STICKY_EW, 
                        padx=GUIConfig.WIDGET_PADX, pady=5)
        combo_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        GUIConfig.init_fonts()
        label = ctk.CTkLabel(combo_frame, text=label_text, font=GUIConfig.LABEL_FONT)
        label.grid(row=0, column=0, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                  sticky=GUIConfig.STICKY_W)
        
        # Combo box
        combo = ctk.CTkComboBox(
            combo_frame,
            variable=variable,
            values=values,
            width=GUIConfig.DROPDOWN_WIDTH,
            command=command,
            state="readonly"
        )
        combo.grid(row=0, column=1, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                  sticky=GUIConfig.STICKY_EW)
        
        return combo_frame, label, combo
    
    @staticmethod
    def create_button_group(parent, buttons_config, row=0):
        """Create a group of buttons with consistent styling
        
        Args:
            buttons_config: List of dicts with 'text', 'command', 'width' keys
        """
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, sticky=GUIConfig.STICKY_EW, 
                         padx=GUIConfig.WIDGET_PADX, pady=5)
        
        buttons = []
        for i, config in enumerate(buttons_config):
            button = ctk.CTkButton(
                button_frame,
                text=config.get('text', ''),
                command=config.get('command', None),
                width=config.get('width', GUIConfig.BUTTON_WIDTH)
            )
            button.grid(row=0, column=i, padx=10, pady=10, sticky=GUIConfig.STICKY_W)
            buttons.append(button)
        
        return button_frame, buttons
    
    @staticmethod
    def create_color_picker_button(parent, label_text, color_var, row=0):
        """Create a color picker button with preview"""
        # Create container frame
        color_frame = ctk.CTkFrame(parent)
        color_frame.grid(row=row, column=0, columnspan=2, sticky=GUIConfig.STICKY_EW, 
                        padx=GUIConfig.WIDGET_PADX, pady=5)
        color_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        GUIConfig.init_fonts()
        label = ctk.CTkLabel(color_frame, text=label_text, font=GUIConfig.LABEL_FONT)
        label.grid(row=0, column=0, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                  sticky=GUIConfig.STICKY_W)
        
        def pick_color():
            color = colorchooser.askcolor(title="Choose QR Code Color")[1]
            if color:
                color_var.set(color)
                button.configure(fg_color=color)
        
        # Color button
        button = ctk.CTkButton(
            color_frame,
            text="Choose Color",
            command=pick_color,
            fg_color=color_var.get() if color_var.get() else "#000000",
            width=120
        )
        button.grid(row=0, column=1, padx=GUIConfig.WIDGET_PADX, pady=GUIConfig.WIDGET_PADY, 
                   sticky=GUIConfig.STICKY_W)
        
        return color_frame, label, button