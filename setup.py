"""
cx_Freeze setup script for QR Generator
Alternative packaging method to PyInstaller
"""

import sys
import os
from cx_Freeze import setup, Executable
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Build options
build_options = {
    # Packages to include
    'packages': [
        'customtkinter',
        'tkinter',
        'PIL', 
        'qrcode',
        'tqdm',
        'colorama',
        'darkdetect',
        'packaging',
        'xml.etree.ElementTree',
        'csv',
        'os',
        'zipfile',
        're',
        'datetime',
        'json',
    ],
    
    # Additional modules to include
    'includes': [
        'src.validation',
        'src.preset_manager', 
        'src.qr_core',
        'src.file_utils',
        'src.gui_config',
        'src.results_viewer',
        'src.mode_handlers',
        'src.progress_handler',
        'src.form_validator',
        'src.config_manager',
        'src.menu_manager',
    ],
    
    # Files and directories to include
    'include_files': [
        ('app_icon.ico', 'app_icon.ico'),
        ('icon_16.png', 'icon_16.png'),
        ('icon_32.png', 'icon_32.png'),
        ('icon_48.png', 'icon_48.png'),
        ('icon_64.png', 'icon_64.png'),
        ('icon_128.png', 'icon_128.png'),
        ('icon_256.png', 'icon_256.png'),
        ('input', 'input'),
        ('presets', 'presets'),
        ('src', 'src'),
        ('README.md', 'README.md'),
        ('SETUP.md', 'SETUP.md'),
        ('CLAUDE.md', 'CLAUDE.md'),
    ],
    
    # Modules to exclude (reduce size)
    'excludes': [
        'matplotlib',
        'numpy', 
        'scipy',
        'pandas',
        'pytest',
        'unittest',
        'test',
        'tests',
    ],
    
    # Additional optimization
    'optimize': 2,
    'zip_include_packages': ['*'],
    'zip_exclude_packages': [],
}

# Base settings for different platforms
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # Hide console window on Windows

# Executable configuration
executables = [
    Executable(
        script='qr_generator.py',
        base=base,
        icon='app_icon.ico' if sys.platform == 'win32' else 'icon_256.png',
        target_name='QRGenerator.exe' if sys.platform == 'win32' else 'QRGenerator',
        copyright='QR Generator Pro v2.0',
        trademarks='QR Generator Pro'
    )
]

# Setup configuration
setup(
    name='QRGenerator',
    version='2.0.0',
    description='Professional QR Code Generation Tool',
    long_description="""
    QR Generator Pro is a comprehensive tool for generating QR codes with advanced features:
    
    • Modern CustomTkinter GUI interface
    • Multiple generation modes (Manual, CSV Import)
    • Support for PNG and SVG output formats
    • Advanced QR code parameters and validation
    • Preset management for repeated use
    • Results viewer with thumbnails
    • Cross-platform compatibility
    """,
    author='QR Generator Pro Team',
    url='https://github.com/andersekbom/qr-generator',
    license='MIT',
    options={'build_exe': build_options},
    executables=executables,
)