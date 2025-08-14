# -*- mode: python ; coding: utf-8 -*-
# PyInstaller specification file for QR Generator
# Generated for cross-platform packaging

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

block_cipher = None

# Analysis phase - collect all Python files and dependencies
a = Analysis(
    # Main application entry point
    ['qr_generator.py'],
    
    # Additional paths to search for modules
    pathex=[str(project_root)],
    
    # Binary dependencies (auto-detected, but can add manual ones)
    binaries=[],
    
    # Data files to include in the bundle
    datas=[
        # Icons and images
        ('app_icon.ico', '.'),
        ('icon_*.png', '.'),
        
        # Sample data and input files
        ('input', 'input'),
        
        # Preset files (if any exist)
        ('presets', 'presets'),
        
        # Include the entire src module directory
        ('src', 'src'),
        
        # Documentation files
        ('README.md', '.'),
        ('SETUP.md', '.'),
        ('CLAUDE.md', '.'),
    ],
    
    # Hidden imports (modules not auto-detected by PyInstaller)
    hiddenimports=[
        # CustomTkinter and its dependencies
        'customtkinter',
        'darkdetect',
        'packaging',
        
        # Standard library modules that might be missed
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        'tkinter.ttk',
        
        # PIL/Pillow imaging
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL.ImageDraw',
        
        # XML processing
        'xml.etree.ElementTree',
        
        # Our modular components
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
    
    # Modules to exclude (reduce bundle size)
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'unittest',
        'test',
        'tests',
    ],
    
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ phase - create Python archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# EXE phase - create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='QRGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    console=False,  # Windows: hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    
    # Platform-specific icon
    icon='app_icon.ico' if sys.platform == 'win32' else 'icon_256.png',
)

# COLLECT phase - bundle everything together
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='QRGenerator'
)

# macOS: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='QRGenerator.app',
        icon='icon_256.png',
        bundle_identifier='com.qrgenerator.app',
        info_plist={
            'CFBundleName': 'QR Generator Pro',
            'CFBundleDisplayName': 'QR Generator Pro',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': 'QRGEN',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'CSV File',
                    'CFBundleTypeExtensions': ['csv'],
                    'CFBundleTypeRole': 'Viewer',
                }
            ]
        },
    )