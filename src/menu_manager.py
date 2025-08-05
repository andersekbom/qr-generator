"""
Menu Manager Module for QR Generator Application

This module provides a data-driven approach to menu creation, eliminating
repetitive code and making menu management more maintainable.
"""

import tkinter as tk
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Data class for menu item configuration"""
    label: str
    command: Optional[Callable] = None
    accelerator: Optional[str] = None
    is_separator: bool = False
    submenu: Optional[List['MenuItem']] = None
    enabled: bool = True
    
    def __post_init__(self):
        """Validate menu item configuration"""
        if not self.is_separator and not self.command and not self.submenu:
            raise ValueError(f"Menu item '{self.label}' must have either command or submenu")


class MenuManager:
    """Data-driven menu management system"""
    
    def __init__(self, root_widget):
        self.root_widget = root_widget
        self.menubar = None
        self.menus = {}
    
    def create_menubar(self, menu_config: Dict[str, List[MenuItem]]) -> tk.Menu:
        """
        Create menu bar from configuration
        
        Args:
            menu_config: Dictionary mapping menu names to list of menu items
            
        Returns:
            Created menubar widget
        """
        self.menubar = tk.Menu(self.root_widget)
        self.root_widget.configure(menu=self.menubar)
        
        for menu_name, menu_items in menu_config.items():
            menu = self._create_menu(menu_items)
            self.menubar.add_cascade(label=menu_name, menu=menu)
            self.menus[menu_name] = menu
        
        return self.menubar
    
    def _create_menu(self, menu_items: List[MenuItem]) -> tk.Menu:
        """Create a menu from list of menu items"""
        menu = tk.Menu(self.menubar, tearoff=0)
        
        for item in menu_items:
            if item.is_separator:
                menu.add_separator()
            elif item.submenu:
                submenu = self._create_menu(item.submenu)
                menu.add_cascade(label=item.label, menu=submenu)
            else:
                state = "normal" if item.enabled else "disabled"
                menu.add_command(
                    label=item.label,
                    command=item.command,
                    accelerator=item.accelerator,
                    state=state
                )
        
        return menu
    
    def update_menu_item_state(self, menu_name: str, item_label: str, enabled: bool):
        """Update the enabled state of a specific menu item"""
        if menu_name in self.menus:
            menu = self.menus[menu_name]
            # Find and update the menu item
            for i in range(menu.index("end") + 1):
                try:
                    if menu.entrycget(i, "label") == item_label:
                        state = "normal" if enabled else "disabled"
                        menu.entryconfig(i, state=state)
                        break
                except tk.TclError:
                    # Skip separators and other non-command items
                    continue
    
    def get_menu(self, menu_name: str) -> Optional[tk.Menu]:
        """Get a specific menu by name"""
        return self.menus.get(menu_name)


class QRGeneratorMenuConfig:
    """Menu configuration for QR Generator application"""
    
    @staticmethod
    def get_menu_config(app) -> Dict[str, List[MenuItem]]:
        """
        Get complete menu configuration for QR Generator
        
        Args:
            app: Reference to the main application for command binding
            
        Returns:
            Dictionary of menu configuration
        """
        return {
            "File": [
                MenuItem("New Session", app.new_session, "Ctrl+N"),
                MenuItem("", is_separator=True),
                MenuItem("Open CSV...", app.browse_csv_file, "Ctrl+O"),
                MenuItem("", is_separator=True),
                MenuItem("Generate QR Codes", app.generate_qr_codes, "Ctrl+G"),
                MenuItem("", is_separator=True),
                MenuItem("Exit", app.root.quit, "Ctrl+Q")
            ],
            
            "Edit": [
                MenuItem("Clear Form", app.clear_form, "Ctrl+R"),
                MenuItem("", is_separator=True),
                MenuItem("Load Preset...", app.load_preset_dialog, "Ctrl+L"),
                MenuItem("Save Preset...", app.save_preset_dialog, "Ctrl+S")
            ],
            
            "View": [
                MenuItem("Toggle Theme", app.toggle_theme, "Ctrl+T"),
                MenuItem("", is_separator=True),
                MenuItem("Clear Results", app.clear_results, "Ctrl+Shift+C"),
                MenuItem("Open Output Folder", app.open_output_folder, "Ctrl+Shift+O")
            ],
            
            "Help": [
                MenuItem("About", app.show_about, "F1")
            ]
        }
    
    @staticmethod
    def setup_keyboard_shortcuts(app):
        """Setup keyboard shortcuts for menu items"""
        shortcuts = {
            '<Control-n>': app.new_session,
            '<Control-o>': lambda e: app.browse_csv_file(),
            '<Control-g>': lambda e: app.generate_qr_codes(),
            '<Control-q>': lambda e: app.root.quit(),
            '<Control-r>': lambda e: app.clear_form(),
            '<Control-l>': lambda e: app.load_preset_dialog(),
            '<Control-s>': lambda e: app.save_preset_dialog(),
            '<Control-t>': lambda e: app.toggle_theme(),
            '<Control-Shift-C>': lambda e: app.clear_results(),
            '<Control-Shift-O>': lambda e: app.open_output_folder(),
            '<F1>': lambda e: app.show_about()
        }
        
        for key, command in shortcuts.items():
            app.root.bind(key, command)


class DynamicMenuManager(MenuManager):
    """Enhanced menu manager with dynamic menu updates"""
    
    def __init__(self, root_widget):
        super().__init__(root_widget)
        self.menu_config = {}
        self.app_ref = None
    
    def set_app_reference(self, app):
        """Set reference to main application"""
        self.app_ref = app
    
    def create_qr_generator_menus(self, app) -> tk.Menu:
        """Create QR Generator specific menus"""
        self.set_app_reference(app)
        self.menu_config = QRGeneratorMenuConfig.get_menu_config(app)
        
        # Create menubar
        menubar = self.create_menubar(self.menu_config)
        
        # Setup keyboard shortcuts
        QRGeneratorMenuConfig.setup_keyboard_shortcuts(app)
        
        return menubar
    
    def update_context_sensitive_items(self, context: Dict[str, Any]):
        """
        Update menu items based on application context
        
        Args:
            context: Dictionary containing application state information
        """
        # Enable/disable Generate based on form validity
        if "form_valid" in context:
            self.update_menu_item_state("File", "Generate QR Codes", context["form_valid"])
        
        # Enable/disable CSV operations based on mode
        if "operation_mode" in context:
            csv_mode = context["operation_mode"] == "csv"
            self.update_menu_item_state("File", "Open CSV...", csv_mode)
        
        # Enable/disable result operations based on results availability
        if "has_results" in context:
            has_results = context["has_results"]
            self.update_menu_item_state("View", "Clear Results", has_results)
            self.update_menu_item_state("View", "Open Output Folder", has_results)
    
    def add_recent_files_menu(self, recent_files: List[str]):
        """Add recent files submenu to File menu (future enhancement)"""
        if not recent_files:
            return
        
        # Add recent files as submenu items
        recent_items = [
            MenuItem("", is_separator=True),
            MenuItem("Recent Files", submenu=[
                MenuItem(file, lambda f=file: self._open_recent_file(f))
                for file in recent_files[:5]  # Limit to 5 recent files
            ])
        ]
        
        # This would require rebuilding the File menu
        # Implementation could be added as needed
    
    def _open_recent_file(self, file_path: str):
        """Handle opening recent file"""
        if self.app_ref and hasattr(self.app_ref, 'open_csv_file'):
            self.app_ref.open_csv_file(file_path)