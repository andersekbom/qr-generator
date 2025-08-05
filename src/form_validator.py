"""
Form Validation Module for QR Generator Application

This module provides a rule-based validation system that eliminates repetitive
validation code and provides a clean, maintainable approach to form validation.
"""

from typing import Dict, List, Tuple, Any, Callable, Optional
from abc import ABC, abstractmethod


class ValidationRule(ABC):
    """Abstract base class for validation rules"""
    
    def __init__(self, field_name: str, error_message: str = None):
        self.field_name = field_name
        self.error_message = error_message or f"{field_name} is invalid"
    
    @abstractmethod
    def validate(self, value: Any) -> Tuple[bool, str]:
        """
        Validate a value against this rule
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class RequiredRule(ValidationRule):
    """Rule to check if a field is not empty"""
    
    def __init__(self, field_name: str):
        super().__init__(field_name, f"{field_name} is required")
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        if not str(value).strip():
            return False, self.error_message
        return True, ""


class IntegerRule(ValidationRule):
    """Rule to validate integer fields with optional min/max bounds"""
    
    def __init__(self, field_name: str, min_value: int = None, max_value: int = None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(field_name, f"{field_name} must be a valid number")
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        try:
            int_value = int(str(value).strip())
            
            if self.min_value is not None and int_value < self.min_value:
                return False, f"{self.field_name} must be at least {self.min_value}"
            
            if self.max_value is not None and int_value > self.max_value:
                return False, f"{self.field_name} must be at most {self.max_value}"
            
            return True, ""
        except (ValueError, TypeError):
            return False, self.error_message


class FloatRule(ValidationRule):
    """Rule to validate float fields with optional min/max bounds"""
    
    def __init__(self, field_name: str, min_value: float = None, max_value: float = None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(field_name, f"{field_name} must be a valid number")
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        try:
            float_value = float(str(value).strip())
            
            if self.min_value is not None and float_value < self.min_value:
                return False, f"{self.field_name} must be at least {self.min_value}"
            
            if self.max_value is not None and float_value > self.max_value:
                return False, f"{self.field_name} must be at most {self.max_value}"
            
            return True, ""
        except (ValueError, TypeError):
            return False, self.error_message


class CustomRule(ValidationRule):
    """Rule that uses a custom validation function"""
    
    def __init__(self, field_name: str, validator_func: Callable[[Any], Tuple[bool, str]]):
        self.validator_func = validator_func
        super().__init__(field_name)
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        return self.validator_func(value)


class ConditionalRule(ValidationRule):
    """Rule that only applies when a condition is met"""
    
    def __init__(self, field_name: str, rule: ValidationRule, condition_func: Callable[[], bool]):
        self.rule = rule
        self.condition_func = condition_func
        super().__init__(field_name, rule.error_message)
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        if self.condition_func():
            return self.rule.validate(value)
        return True, ""  # Skip validation if condition not met


class FormValidator:
    """Rule-based form validator"""
    
    def __init__(self):
        self.field_rules: Dict[str, List[ValidationRule]] = {}
    
    def add_rule(self, field_name: str, rule: ValidationRule):
        """Add a validation rule for a field"""
        if field_name not in self.field_rules:
            self.field_rules[field_name] = []
        self.field_rules[field_name].append(rule)
    
    def add_required(self, field_name: str):
        """Add required validation for a field"""
        self.add_rule(field_name, RequiredRule(field_name))
    
    def add_integer(self, field_name: str, min_value: int = None, max_value: int = None):
        """Add integer validation for a field"""
        self.add_rule(field_name, IntegerRule(field_name, min_value, max_value))
    
    def add_float(self, field_name: str, min_value: float = None, max_value: float = None):
        """Add float validation for a field"""
        self.add_rule(field_name, FloatRule(field_name, min_value, max_value))
    
    def add_custom(self, field_name: str, validator_func: Callable[[Any], Tuple[bool, str]]):
        """Add custom validation for a field"""
        self.add_rule(field_name, CustomRule(field_name, validator_func))
    
    def add_conditional(self, field_name: str, rule: ValidationRule, condition_func: Callable[[], bool]):
        """Add conditional validation for a field"""
        self.add_rule(field_name, ConditionalRule(field_name, rule, condition_func))
    
    def validate_field(self, field_name: str, value: Any) -> Tuple[bool, str]:
        """Validate a single field against all its rules"""
        if field_name not in self.field_rules:
            return True, ""
        
        for rule in self.field_rules[field_name]:
            is_valid, error_message = rule.validate(value)
            if not is_valid:
                return False, error_message
        
        return True, ""
    
    def validate_form(self, field_values: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """
        Validate entire form
        
        Returns:
            Tuple of (is_valid, first_error_message, all_error_messages)
        """
        all_errors = []
        
        for field_name, value in field_values.items():
            is_valid, error_message = self.validate_field(field_name, value)
            if not is_valid:
                all_errors.append(error_message)
        
        if all_errors:
            return False, all_errors[0], all_errors
        
        return True, "", []


class QRFormValidator(FormValidator):
    """Specialized form validator for QR Generator forms"""
    
    def __init__(self, gui_app):
        super().__init__()
        self.gui_app = gui_app
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Setup validation rules specific to QR Generator"""
        
        # Manual mode fields (conditional on manual mode)
        manual_condition = lambda: self.gui_app.operation_mode.get() == "manual"
        
        self.add_conditional("Valid Uses", 
                           RequiredRule("Valid Uses"), 
                           manual_condition)
        self.add_conditional("Valid Uses", 
                           IntegerRule("Valid Uses", min_value=1), 
                           manual_condition)
        
        self.add_conditional("Volume", 
                           RequiredRule("Volume"), 
                           manual_condition)
        self.add_conditional("Volume", 
                           IntegerRule("Volume", min_value=1), 
                           manual_condition)
        
        self.add_conditional("End Date", 
                           RequiredRule("End Date"), 
                           manual_condition)
        
        self.add_conditional("Color", 
                           RequiredRule("Color"), 
                           manual_condition)
        
        # Add custom date validation
        def validate_date(value):
            from src.validation import validate_date_format
            if not validate_date_format(str(value)):
                return False, "Invalid date format. Use DD.MM.YY"
            return True, ""
        
        self.add_conditional("End Date",
                           CustomRule("End Date", validate_date),
                           manual_condition)
        
        # Add custom color validation  
        def validate_color(value):
            from src.validation import validate_color_format
            is_valid, error_msg = validate_color_format(str(value))
            return is_valid, error_msg
        
        self.add_conditional("Color",
                           CustomRule("Color", validate_color),
                           manual_condition)
        
        self.add_conditional("Security Code", 
                           RequiredRule("Security Code"), 
                           manual_condition)
        
        self.add_conditional("Suffix Code", 
                           RequiredRule("Suffix Code"), 
                           manual_condition)
        
        self.add_conditional("Count", 
                           IntegerRule("Count", min_value=1), 
                           manual_condition)
        
        # CSV mode fields (conditional on CSV mode)
        csv_condition = lambda: self.gui_app.operation_mode.get() == "csv"
        
        self.add_conditional("CSV File", 
                           RequiredRule("CSV File"), 
                           csv_condition)
        
        # Always required fields
        self.add_required("Output Directory")
        
        # Advanced fields with bounds
        self.add_integer("Box Size", min_value=1, max_value=50)
        self.add_integer("Border", min_value=0, max_value=20)
        self.add_integer("PNG Quality", min_value=1, max_value=100)
        self.add_float("SVG Scale", min_value=0.1, max_value=10.0)
    
    def validate_current_form(self) -> Tuple[bool, str]:
        """Validate the current form state"""
        field_values = self._collect_field_values()
        is_valid, first_error, _ = self.validate_form(field_values)
        return is_valid, first_error
    
    def _collect_field_values(self) -> Dict[str, Any]:
        """Collect current field values from the GUI"""
        values = {}
        
        # Manual mode fields
        if self.gui_app.operation_mode.get() == "manual":
            values["Valid Uses"] = self.gui_app.valid_uses.get()
            values["Volume"] = self.gui_app.volume.get()
            values["End Date"] = self.gui_app.end_date.get()
            values["Color"] = self.gui_app.color.get()
            values["Security Code"] = self.gui_app.security_code.get()
            values["Suffix Code"] = self.gui_app.suffix_code.get()
            values["Count"] = self.gui_app.count.get()
        
        # CSV mode fields
        if self.gui_app.operation_mode.get() == "csv":
            values["CSV File"] = self.gui_app.csv_file_path.get()
        
        # Common fields
        values["Output Directory"] = self.gui_app.output_directory.get()
        values["Box Size"] = self.gui_app.box_size.get()
        values["Border"] = self.gui_app.border.get()
        
        if self.gui_app.format.get() == "png":
            values["PNG Quality"] = self.gui_app.png_quality.get()
        elif self.gui_app.format.get() == "svg":
            values["SVG Scale"] = self.gui_app.svg_precision.get()
        
        return values