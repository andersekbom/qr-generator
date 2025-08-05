"""
Configuration Manager Module for QR Generator Application

This module provides centralized configuration management including:
- Application settings persistence
- Window state management  
- User preferences handling
- Theme and UI state management
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, app_name: str = "qr_generator"):
        self.app_name = app_name
        self._config_cache = {}
        self._config_path = None
    
    def get_config_path(self) -> str:
        """Get path for configuration file"""
        if self._config_path is None:
            try:
                config_dir = Path.home() / f".{self.app_name}"
                config_dir.mkdir(exist_ok=True)
                self._config_path = str(config_dir / "config.json")
            except Exception:
                # Fallback to current directory
                self._config_path = f"{self.app_name}_config.json"
        
        return self._config_path
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = self.get_config_path()
        
        if not os.path.exists(config_path):
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._config_cache = config
                return config
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            config_path = self.get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self._config_cache = config
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a specific configuration section"""
        if not self._config_cache:
            self._config_cache = self.load_config()
        
        return self._config_cache.get(section_name, {})
    
    def set_section(self, section_name: str, section_data: Dict[str, Any]) -> bool:
        """Set a specific configuration section"""
        if not self._config_cache:
            self._config_cache = self.load_config()
        
        self._config_cache[section_name] = section_data
        return self.save_config(self._config_cache)
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        section_data = self.get_section(section)
        return section_data.get(key, default)
    
    def set_value(self, section: str, key: str, value: Any) -> bool:
        """Set a specific configuration value"""
        if not self._config_cache:
            self._config_cache = self.load_config()
        
        if section not in self._config_cache:
            self._config_cache[section] = {}
        
        self._config_cache[section][key] = value
        return self.save_config(self._config_cache)


class QRGeneratorConfig(ConfigManager):
    """Specialized configuration manager for QR Generator"""
    
    def __init__(self):
        super().__init__("qr_generator")
        self.gui_app = None
    
    def set_gui_app(self, gui_app):
        """Set reference to GUI application for collecting current values"""
        self.gui_app = gui_app
    
    def collect_current_settings(self) -> Dict[str, Any]:
        """Collect current settings from GUI application"""
        if not self.gui_app:
            return {}
        
        try:
            return {
                "window": {
                    "geometry": self.gui_app.root.geometry(),
                    "theme": self._get_current_theme()
                },
                "last_settings": {
                    "operation_mode": self.gui_app.operation_mode.get(),
                    "valid_uses": self.gui_app.valid_uses.get(),
                    "volume": self.gui_app.volume.get(),
                    "end_date": self.gui_app.end_date.get(),
                    "color": self.gui_app.color.get(),
                    "security_code": self.gui_app.security_code.get(),
                    "suffix_code": self.gui_app.suffix_code.get(),
                    "count": self.gui_app.count.get(),
                    "format": self.gui_app.format.get(),
                    "png_quality": self.gui_app.png_quality.get(),
                    "svg_precision": self.gui_app.svg_precision.get(),
                    "qr_version": self.gui_app.qr_version.get(),
                    "error_correction": self.gui_app.error_correction.get(),
                    "box_size": self.gui_app.box_size.get(),
                    "border": self.gui_app.border.get(),
                    "filename_prefix": self.gui_app.filename_prefix.get(),
                    "filename_suffix": self.gui_app.filename_suffix.get(),
                    "use_payload_filename": self.gui_app.use_payload_filename.get(),
                    "output_directory": self.gui_app.output_directory.get(),
                    "create_zip": self.gui_app.create_zip.get(),
                    "cleanup_temp": self.gui_app.cleanup_temp.get()
                },
                "ui_preferences": {
                    "last_csv_path": getattr(self.gui_app, 'last_csv_path', ''),
                    "selected_preset": self.gui_app.selected_preset.get(),
                    "csv_file_path": self.gui_app.csv_file_path.get()
                }
            }
        except Exception as e:
            print(f"Error collecting current settings: {e}")
            return {}
    
    def _get_current_theme(self) -> str:
        """Get current theme"""
        try:
            import customtkinter as ctk
            return ctk.get_appearance_mode().lower()
        except Exception:
            return "system"
    
    def save_current_settings(self) -> bool:
        """Save current GUI settings to configuration file"""
        settings = self.collect_current_settings()
        if settings:
            return self.save_config(settings)
        return False
    
    def restore_settings_to_gui(self) -> bool:
        """Restore saved settings to GUI application"""
        if not self.gui_app:
            return False
        
        config = self.load_config()
        if not config:
            return False
        
        try:
            # Restore window settings
            self._restore_window_settings(config.get("window", {}))
            
            # Restore last settings
            self._restore_form_settings(config.get("last_settings", {}))
            
            # Restore UI preferences
            self._restore_ui_preferences(config.get("ui_preferences", {}))
            
            return True
        except Exception as e:
            print(f"Error restoring settings: {e}")
            return False
    
    def _restore_window_settings(self, window_config: Dict[str, Any]):
        """Restore window-specific settings"""
        if not window_config:
            return
        
        # Restore geometry
        if "geometry" in window_config:
            try:
                self.gui_app.root.geometry(window_config["geometry"])
            except Exception:
                pass  # Invalid geometry, use default
        
        # Restore theme
        if "theme" in window_config:
            try:
                import customtkinter as ctk
                ctk.set_appearance_mode(window_config["theme"])
            except Exception:
                pass  # Invalid theme, use default
    
    def _restore_form_settings(self, settings: Dict[str, Any]):
        """Restore form field settings"""
        if not settings:
            return
        
        # Restore each setting if it exists
        for key, value in settings.items():
            if hasattr(self.gui_app, key):
                try:
                    getattr(self.gui_app, key).set(value)
                except Exception:
                    pass  # Invalid value, keep default
    
    def _restore_ui_preferences(self, preferences: Dict[str, Any]):
        """Restore UI preferences"""
        if not preferences:
            return
        
        if "last_csv_path" in preferences:
            self.gui_app.last_csv_path = preferences["last_csv_path"]
        
        if "selected_preset" in preferences:
            try:
                self.gui_app.selected_preset.set(preferences["selected_preset"])
            except Exception:
                pass
        
        if "csv_file_path" in preferences:
            try:
                self.gui_app.csv_file_path.set(preferences["csv_file_path"])
            except Exception:
                pass
    
    def get_window_geometry(self) -> Optional[str]:
        """Get saved window geometry"""
        return self.get_value("window", "geometry")
    
    def get_theme(self) -> str:
        """Get saved theme"""
        return self.get_value("window", "theme", "system")
    
    def get_last_csv_path(self) -> str:
        """Get last used CSV file path"""
        return self.get_value("ui_preferences", "last_csv_path", "")
    
    def set_last_csv_path(self, path: str) -> bool:
        """Set last used CSV file path"""
        return self.set_value("ui_preferences", "last_csv_path", path)
    
    def get_form_defaults(self) -> Dict[str, Any]:
        """Get default form values from saved settings"""
        return self.get_section("last_settings")


class SettingsManager:
    """High-level settings management interface"""
    
    def __init__(self, config_manager: QRGeneratorConfig):
        self.config = config_manager
    
    def auto_save_on_change(self, gui_app):
        """Setup automatic saving when settings change"""
        self.config.set_gui_app(gui_app)
        
        # Could add variable traces here to auto-save on changes
        # For now, we'll rely on manual save calls
    
    def save_session(self) -> bool:
        """Save current session settings"""
        return self.config.save_current_settings()
    
    def restore_session(self) -> bool:
        """Restore previous session settings"""
        return self.config.restore_settings_to_gui()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            config_path = self.config.get_config_path()
            if os.path.exists(config_path):
                os.remove(config_path)
            return True
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False