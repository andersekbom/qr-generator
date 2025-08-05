"""
Progress Handler Module for QR Generator Application

This module provides centralized progress and status management for the QR Generator.
It handles status updates, progress indicators, and UI refresh operations.
"""

from enum import Enum
from typing import Optional, Any


class StatusType(Enum):
    """Status message types with associated colors"""
    INFO = "blue"
    SUCCESS = "green"
    WARNING = "orange"
    ERROR = "red"
    NEUTRAL = "gray"
    

class ProgressHandler:
    """Centralized progress and status management"""
    
    def __init__(self, status_label, root_widget):
        """
        Initialize progress handler
        
        Args:
            status_label: The status label widget to update
            root_widget: The root widget for UI refresh operations
        """
        self.status_label = status_label
        self.root_widget = root_widget
        self._current_operation = None
        self._managed_buttons = {}
    
    def update_status(self, message: str, status_type: StatusType = StatusType.NEUTRAL, 
                     refresh_ui: bool = False):
        """
        Update status message with appropriate color
        
        Args:
            message: Status message to display
            status_type: Type of status (affects color)
            refresh_ui: Whether to refresh the UI after update
        """
        try:
            self.status_label.configure(text=message, text_color=status_type.value)
            if refresh_ui:
                self.root_widget.update()
        except Exception as e:
            # Fallback in case of widget errors
            print(f"Status update failed: {e}")
    
    def show_info(self, message: str, refresh_ui: bool = False):
        """Show informational message"""
        self.update_status(message, StatusType.INFO, refresh_ui)
    
    def show_success(self, message: str, refresh_ui: bool = False):
        """Show success message"""
        self.update_status(message, StatusType.SUCCESS, refresh_ui)
    
    def show_warning(self, message: str, refresh_ui: bool = False):
        """Show warning message"""
        self.update_status(message, StatusType.WARNING, refresh_ui)
    
    def show_error(self, message: str, refresh_ui: bool = False):
        """Show error message"""
        self.update_status(message, StatusType.ERROR, refresh_ui)
    
    def show_ready(self, message: str = "Ready", refresh_ui: bool = False):
        """Show neutral/ready message"""
        self.update_status(message, StatusType.NEUTRAL, refresh_ui)
    
    def start_operation(self, operation_name: str, message: str = None):
        """
        Start a tracked operation with progress indication
        
        Args:
            operation_name: Name of the operation for tracking
            message: Optional custom message (defaults to operation name)
        """
        self._current_operation = operation_name
        display_message = message or f"{operation_name}..."
        self.update_status(display_message, StatusType.INFO, refresh_ui=True)
    
    def update_operation(self, message: str, status_type: StatusType = StatusType.INFO):
        """Update the current operation status"""
        self.update_status(message, status_type, refresh_ui=True)
    
    def complete_operation(self, success_message: str = None, error_message: str = None):
        """
        Complete the current operation
        
        Args:
            success_message: Message to show on success
            error_message: Message to show on error (if None, shows success)
        """
        if error_message:
            self.show_error(error_message)
        elif success_message:
            self.show_success(success_message)
        elif self._current_operation:
            self.show_success(f"✅ {self._current_operation} completed successfully!")
        
        self._current_operation = None
    
    def handle_error(self, error: Exception, context: str = "Operation"):
        """
        Handle and display error with context
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
        """
        error_message = f"❌ {context} failed: {str(error)}"
        self.show_error(error_message)
        self._current_operation = None
    
    def refresh_ui(self):
        """Force UI refresh"""
        try:
            self.root_widget.update()
        except Exception:
            # UI might be destroyed or unavailable
            pass
    
    def reset(self):
        """Reset to neutral state"""
        self._current_operation = None
        self.show_ready("Ready to generate QR codes")
    
    def register_button(self, name: str, button_widget):
        """
        Register a button for state management
        
        Args:
            name: Name identifier for the button
            button_widget: The button widget to manage
        """
        self._managed_buttons[name] = button_widget
    
    def enable_button(self, name: str):
        """
        Enable a managed button
        
        Args:
            name: Name of the button to enable
        """
        if name in self._managed_buttons:
            try:
                self._managed_buttons[name].configure(state="normal")
            except Exception:
                pass  # Button may not exist or be accessible
    
    def disable_button(self, name: str):
        """
        Disable a managed button
        
        Args:
            name: Name of the button to disable
        """
        if name in self._managed_buttons:
            try:
                self._managed_buttons[name].configure(state="disabled")
            except Exception:
                pass  # Button may not exist or be accessible
    
    def set_button_state(self, name: str, enabled: bool):
        """
        Set button state based on boolean
        
        Args:
            name: Name of the button
            enabled: True to enable, False to disable
        """
        if enabled:
            self.enable_button(name)
        else:
            self.disable_button(name)


class ValidationProgressHandler(ProgressHandler):
    """Specialized progress handler for form validation"""
    
    def show_validation_success(self):
        """Show validation success state"""
        self.show_ready("Ready to generate QR codes")
    
    def show_validation_error(self, field_errors: list):
        """Show validation errors"""
        if len(field_errors) == 1:
            self.show_warning(f"Form incomplete: {field_errors[0]}")
        else:
            self.show_warning("Form incomplete: Fill all required fields")
    
    def show_validation_in_progress(self):
        """Show validation in progress"""
        self.update_status("Validating inputs...", StatusType.INFO, refresh_ui=True)


class GenerationProgressHandler(ProgressHandler):
    """Specialized progress handler for QR code generation"""
    
    def start_generation(self, count: int = 1, mode: str = "manual"):
        """Start QR code generation progress"""
        if count == 1:
            message = "Generating QR code..."
        else:
            message = f"Generating {count} QR codes..."
        
        if mode == "csv":
            message = f"Generating {count} QR codes from CSV..."
            
        self.start_operation("QR Generation", message)
    
    def update_csv_loading(self):
        """Update status for CSV loading"""
        self.update_operation("Loading CSV file...", StatusType.INFO)
    
    def complete_generation(self, count: int = 1, zip_path: str = None):
        """Complete generation with appropriate success message"""
        if count == 1:
            message = "✅ QR code generated successfully!"
        else:
            message = f"✅ {count} QR codes generated successfully!"
            
        self.show_success(message)
        self._current_operation = None
    
    def show_zip_creation(self, zip_filename: str):
        """Show ZIP creation success"""
        self.show_success(f"✅ ZIP created: {zip_filename}")
    
    def show_cleanup_warning(self, error: Exception):
        """Show cleanup warning"""
        self.show_warning(f"Warning: Cleanup failed: {str(error)}")