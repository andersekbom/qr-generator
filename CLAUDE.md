# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with specific versions
pip install -r requirements.txt

# Verify installation
python -c "import qr_generator; print('✅ Setup complete!')"
```

### Running Applications
- **Main QR code generator**: `python qr_generator.py`

### Testing Commands
```bash
# Test core functionality without GUI
python -c "from src.validation import validate_integer_input; print('✅ Core modules working')"

# Verify modular architecture
python -c "from src.progress_handler import ProgressHandler; from src.form_validator import QRFormValidator; print('✅ Refactored modules functional')"
```

## Architecture Overview

This is a **modular Python-based QR code generation application** with a modern, maintainable architecture. The project was comprehensively refactored from a monolithic 3,244-line file into a clean, modular system.

### 🏗️ Current Architecture (Post-Refactoring)

#### Main Application
- **`qr_generator.py`** (1,708 lines) - Main GUI application and orchestration
  - Modern CustomTkinter-based interface
  - Modular component integration
  - Clean separation of concerns

#### 📦 Core Modules (`src/` directory)

##### Phase 1 Modules (Core Functionality):
- **`validation.py`** - Input validation functions
- **`preset_manager.py`** - Settings presets management
- **`qr_core.py`** - QR code generation engine
- **`file_utils.py`** - File operations and utilities

##### Phase 2 Modules (GUI Components):
- **`gui_config.py`** - GUI configuration and widget factory
- **`results_viewer.py`** - Results display and thumbnails
- **`mode_handlers.py`** - Mode-specific logic (Manual/CSV)

##### Phase 4 Modules (Quality & Management):
- **`progress_handler.py`** - Centralized status and progress management
- **`form_validator.py`** - Rule-based validation system
- **`config_manager.py`** - Unified configuration management
- **`menu_manager.py`** - Data-driven menu system

### 🎯 Design Patterns Implemented

- **Factory Pattern** - Mode handler creation (`ModeHandlerFactory`)
- **Strategy Pattern** - Validation rules (`ValidationRule` hierarchy)
- **Observer Pattern** - Progress and status handling
- **Singleton Pattern** - Configuration management
- **Data-driven Configuration** - Menu and UI systems

### 🔧 Key Features

#### Operation Modes:
1. **Manual Mode** - Individual parameter input for batch generation
2. **CSV Mode** - Bulk generation from CSV files with auto-delimiter detection

#### Output Formats:
- **PNG** - High-quality raster images with quality control
- **SVG** - Scalable vector graphics with precision settings

#### Advanced Features:
- Real-time form validation with visual feedback
- Preset system for quick parameter sets
- Automatic ZIP file creation for batch operations
- Theme support (light/dark mode)
- Comprehensive progress tracking
- Results viewer with thumbnail previews

### 📁 File Structure

```
qr-generator/
├── qr_generator.py              # Main GUI application (1,708 lines)
├── src/                         # Modular components (11 files, 2,435 lines)
│   ├── validation.py            # Input validation functions
│   ├── preset_manager.py        # Settings presets
│   ├── qr_core.py              # QR generation engine
│   ├── file_utils.py           # File operations
│   ├── gui_config.py           # GUI configuration
│   ├── results_viewer.py       # Results display
│   ├── mode_handlers.py        # Mode-specific logic
│   ├── progress_handler.py     # Status management
│   ├── form_validator.py       # Rule-based validation
│   ├── config_manager.py       # Configuration system
│   └── menu_manager.py         # Menu management
├── presets/                     # Saved parameter presets
├── input/                      # CSV input files
├── output/                     # Temporary generation directory
├── requirements.txt            # Python dependencies
└── tasks_refactoring.md        # Refactoring documentation
```

### 🚀 Key Libraries

- **`customtkinter`** - Modern GUI framework
- **`qrcode`** - Core QR code generation (PNG/SVG support)
- **`Pillow`** - Image processing and thumbnails
- **`tqdm`** - Progress bars for batch operations

### 💡 Development Guidelines

#### Adding New Features:
1. **Use existing patterns** - Follow the established modular architecture
2. **Leverage validation system** - Use `ValidationRule` classes for form validation
3. **Centralize status updates** - Use `ProgressHandler` for user feedback
4. **Configuration management** - Use `ConfigManager` for persistent settings
5. **Follow separation of concerns** - Keep business logic in specialized modules

#### Code Quality Standards:
- **Modular design** - Each module has a single responsibility
- **Type hints** - Use typing annotations where beneficial
- **Error handling** - Implement proper exception handling
- **Documentation** - Include docstrings for public methods
- **No repetitive patterns** - Use the centralized systems

### 📊 Refactoring Achievements

- **47.3% code reduction** in main file (3,244 → 1,708 lines)
- **11 specialized modules** for clean architecture
- **15/15 refactoring tasks** completed across 4 phases
- **Modern design patterns** implemented throughout
- **Enhanced maintainability** and extensibility
- **Zero breaking changes** - all functionality preserved

### 🔍 Common Operations

#### Testing Module Integration:
```python
# Test progress handler
from src.progress_handler import ProgressHandler, StatusType
handler = ProgressHandler(status_label, root_widget)
handler.update_status("Ready", StatusType.SUCCESS)

# Test form validation
from src.form_validator import QRFormValidator
validator = QRFormValidator(gui_app)
is_valid, error = validator.validate_current_form()

# Test configuration
from src.config_manager import QRGeneratorConfig
config = QRGeneratorConfig()
config.save_current_settings()
```

This modular architecture ensures the application is maintainable, extensible, and follows modern Python development best practices.