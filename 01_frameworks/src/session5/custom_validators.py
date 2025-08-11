# src/session5/custom_validators.py
"""
Advanced custom validation logic for PydanticAI agents.
Implements domain-specific validators, composite validation patterns, and validation utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Type, Union, Pattern
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime, date, timedelta
from enum import Enum
import re
import json
import asyncio
import logging
import phonenumbers
from phonenumbers import NumberParseException
import email_validator
import ipaddress
from urllib.parse import urlparse
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationContext(BaseModel):
    """Context for validation operations."""
    field_name: str = Field(..., description="Name of the field being validated")
    model_name: str = Field(..., description="Name of the model")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User-specific context")
    strict_mode: bool = Field(default=False, description="Whether to use strict validation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# Custom validation exceptions

class ValidationError(ValueError):
    """Enhanced validation error with context."""
    
    def __init__(self, message: str, field_name: str = None, severity: ValidationSeverity = ValidationSeverity.ERROR):
        super().__init__(message)
        self.field_name = field_name
        self.severity = severity
        self.timestamp = datetime.now()

class CompositeValidationError(ValidationError):
    """Error for composite validation failures."""
    
    def __init__(self, errors: List[ValidationError], field_name: str = None):
        self.errors = errors
        messages = [str(e) for e in errors]
        super().__init__(f"Multiple validation errors: {'; '.join(messages)}", field_name)

# Base validator classes

class CustomValidator(ABC):
    """Abstract base class for custom validators."""
    
    def __init__(self, name: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        self.name = name
        self.severity = severity
    
    @abstractmethod
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate a value."""
        pass
    
    def __call__(self, value: Any, context: Optional[ValidationContext] = None) -> Any:
        """Make validator callable."""
        if not self.validate(value, context):
            raise ValidationError(f"{self.name} validation failed", severity=self.severity)
        return value

class RegexValidator(CustomValidator):
    """Validates values against regular expressions."""
    
    def __init__(self, pattern: Union[str, Pattern], name: str = None, **kwargs):
        super().__init__(name or f"regex_{pattern}", **kwargs)
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate against regex pattern."""
        if not isinstance(value, str):
            return False
        return bool(self.pattern.match(value))

# Domain-specific validators

class EmailValidator(CustomValidator):
    """Advanced email validation."""
    
    def __init__(self, check_deliverability: bool = False, **kwargs):
        super().__init__("email", **kwargs)
        self.check_deliverability = check_deliverability
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate email address."""
        if not isinstance(value, str):
            return False
        
        try:
            # Use email-validator library for comprehensive validation
            validation = email_validator.validate_email(value, check_deliverability=self.check_deliverability)
            return True
        except email_validator.EmailNotValidError:
            return False
        except Exception:
            # Fallback to basic regex
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, value))

class PhoneValidator(CustomValidator):
    """International phone number validation."""
    
    def __init__(self, region: str = None, **kwargs):
        super().__init__("phone", **kwargs)
        self.region = region
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate phone number."""
        if not isinstance(value, str):
            return False
        
        try:
            parsed = phonenumbers.parse(value, self.region)
            return phonenumbers.is_valid_number(parsed)
        except NumberParseException:
            return False
        except Exception:
            # Fallback to basic pattern
            pattern = r'^[\+]?[1-9][\d]{0,15}$'
            return bool(re.match(pattern, re.sub(r'[\s\-\(\)]', '', value)))

class URLValidator(CustomValidator):
    """URL validation with scheme and domain checks."""
    
    def __init__(self, allowed_schemes: List[str] = None, require_tld: bool = True, **kwargs):
        super().__init__("url", **kwargs)
        self.allowed_schemes = allowed_schemes or ['http', 'https']
        self.require_tld = require_tld
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate URL."""
        if not isinstance(value, str):
            return False
        
        try:
            parsed = urlparse(value)
            
            # Check scheme
            if parsed.scheme.lower() not in self.allowed_schemes:
                return False
            
            # Check netloc exists
            if not parsed.netloc:
                return False
            
            # Check TLD if required
            if self.require_tld:
                domain_parts = parsed.netloc.split('.')
                if len(domain_parts) < 2 or len(domain_parts[-1]) < 2:
                    return False
            
            return True
        
        except Exception:
            return False

class IPAddressValidator(CustomValidator):
    """IP address validation (IPv4 and IPv6)."""
    
    def __init__(self, version: int = None, **kwargs):
        super().__init__("ip_address", **kwargs)
        self.version = version  # 4, 6, or None for both
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate IP address."""
        if not isinstance(value, str):
            return False
        
        try:
            ip = ipaddress.ip_address(value)
            if self.version is None:
                return True
            elif self.version == 4:
                return isinstance(ip, ipaddress.IPv4Address)
            elif self.version == 6:
                return isinstance(ip, ipaddress.IPv6Address)
            else:
                return False
        except ipaddress.AddressValueError:
            return False

class CreditCardValidator(CustomValidator):
    """Credit card number validation using Luhn algorithm."""
    
    def __init__(self, **kwargs):
        super().__init__("credit_card", **kwargs)
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate credit card using Luhn algorithm."""
        if not isinstance(value, str):
            return False
        
        # Remove spaces and dashes
        number = re.sub(r'[\s\-]', '', value)
        
        # Check if all digits
        if not number.isdigit():
            return False
        
        # Check length (most cards are 13-19 digits)
        if len(number) < 13 or len(number) > 19:
            return False
        
        # Luhn algorithm
        def luhn_check(card_num):
            digits = [int(d) for d in card_num]
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return sum(digits) % 10 == 0
        
        return luhn_check(number)

class PasswordStrengthValidator(CustomValidator):
    """Password strength validation."""
    
    def __init__(self, min_length: int = 8, require_uppercase: bool = True,
                 require_lowercase: bool = True, require_digits: bool = True,
                 require_special: bool = True, **kwargs):
        super().__init__("password_strength", **kwargs)
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate password strength."""
        if not isinstance(value, str):
            return False
        
        if len(value) < self.min_length:
            return False
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            return False
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            return False
        
        if self.require_digits and not re.search(r'\d', value):
            return False
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            return False
        
        return True
    
    def get_strength_score(self, password: str) -> float:
        """Get password strength score (0.0 to 1.0)."""
        if not isinstance(password, str):
            return 0.0
        
        score = 0.0
        max_score = 5.0
        
        # Length score
        if len(password) >= self.min_length:
            score += min(len(password) / 12.0, 1.0)
        
        # Character type scores
        if re.search(r'[A-Z]', password):
            score += 1.0
        if re.search(r'[a-z]', password):
            score += 1.0
        if re.search(r'\d', password):
            score += 1.0
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1.0
        
        return min(score / max_score, 1.0)

class DateRangeValidator(CustomValidator):
    """Validates dates within specified ranges."""
    
    def __init__(self, min_date: date = None, max_date: date = None, **kwargs):
        super().__init__("date_range", **kwargs)
        self.min_date = min_date
        self.max_date = max_date
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate date range."""
        if isinstance(value, datetime):
            value = value.date()
        elif isinstance(value, str):
            try:
                value = datetime.fromisoformat(value).date()
            except ValueError:
                return False
        elif not isinstance(value, date):
            return False
        
        if self.min_date and value < self.min_date:
            return False
        
        if self.max_date and value > self.max_date:
            return False
        
        return True

class BusinessHoursValidator(CustomValidator):
    """Validates time within business hours."""
    
    def __init__(self, start_hour: int = 9, end_hour: int = 17, 
                 business_days: List[int] = None, **kwargs):
        super().__init__("business_hours", **kwargs)
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.business_days = business_days or [0, 1, 2, 3, 4]  # Mon-Fri
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate business hours."""
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError:
                return False
        elif not isinstance(value, datetime):
            return False
        
        # Check business day
        if value.weekday() not in self.business_days:
            return False
        
        # Check business hours
        if value.hour < self.start_hour or value.hour >= self.end_hour:
            return False
        
        return True

# Composite validators

class CompositeValidator(CustomValidator):
    """Combines multiple validators."""
    
    def __init__(self, validators: List[CustomValidator], require_all: bool = True, **kwargs):
        super().__init__("composite", **kwargs)
        self.validators = validators
        self.require_all = require_all
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Validate using composite logic."""
        results = []
        errors = []
        
        for validator in self.validators:
            try:
                result = validator.validate(value, context)
                results.append(result)
            except ValidationError as e:
                results.append(False)
                errors.append(e)
        
        if self.require_all:
            success = all(results)
        else:
            success = any(results)
        
        if not success and errors:
            raise CompositeValidationError(errors)
        
        return success

class ConditionalValidator(CustomValidator):
    """Applies validation based on conditions."""
    
    def __init__(self, condition: Callable[[Any, Optional[ValidationContext]], bool],
                 validator: CustomValidator, **kwargs):
        super().__init__("conditional", **kwargs)
        self.condition = condition
        self.validator = validator
    
    def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
        """Apply conditional validation."""
        if self.condition(value, context):
            return self.validator.validate(value, context)
        return True  # Skip validation if condition not met

# Utility functions and decorators

def create_custom_validator(func: Callable[[Any], bool], name: str = None, 
                          severity: ValidationSeverity = ValidationSeverity.ERROR):
    """Create custom validator from function."""
    
    class FunctionValidator(CustomValidator):
        def __init__(self):
            super().__init__(name or func.__name__, severity)
            self.func = func
        
        def validate(self, value: Any, context: Optional[ValidationContext] = None) -> bool:
            return self.func(value)
    
    return FunctionValidator()

def validate_with(validator: CustomValidator):
    """Decorator to apply custom validator to Pydantic field."""
    
    def decorator(func):
        def wrapper(cls, v, values, **kwargs):
            context = ValidationContext(
                field_name=kwargs.get('field_name', 'unknown'),
                model_name=cls.__name__
            )
            validator(v, context)
            return v
        return validator_decorator(wrapper)
    
    return decorator

# Example model using custom validators

class UserRegistrationModel(BaseModel):
    """Example model with custom validation."""
    
    email: str = Field(..., description="User email address")
    phone: str = Field(..., description="Phone number")
    password: str = Field(..., description="Password")
    website: Optional[str] = Field(None, description="Personal website")
    birth_date: date = Field(..., description="Birth date")
    
    @validator('email')
    def validate_email(cls, v):
        EmailValidator(check_deliverability=False)(v)
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        PhoneValidator()(v)
        return v
    
    @validator('password')
    def validate_password(cls, v):
        PasswordStrengthValidator(min_length=8)(v)
        return v
    
    @validator('website')
    def validate_website(cls, v):
        if v:
            URLValidator()(v)
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        # Must be at least 13 years old
        min_date = date.today() - timedelta(days=120*365)  # ~120 years ago
        max_date = date.today() - timedelta(days=13*365)   # 13 years ago
        DateRangeValidator(min_date=min_date, max_date=max_date)(v)
        return v

# Demonstration and examples

def demo_custom_validators():
    """Demonstrate custom validators."""
    print("\n=== Custom Validators Demo ===")
    
    # Test individual validators
    email_validator = EmailValidator()
    phone_validator = PhoneValidator()
    password_validator = PasswordStrengthValidator()
    url_validator = URLValidator()
    
    print("Testing Email Validator:")
    emails = ["test@example.com", "invalid-email", "user+tag@domain.co.uk"]
    for email in emails:
        try:
            email_validator(email)
            print(f"  ✓ {email}")
        except ValidationError as e:
            print(f"  ✗ {email}: {str(e)}")
    
    print("\nTesting Phone Validator:")
    phones = ["+1-555-123-4567", "555-123-4567", "invalid-phone"]
    for phone in phones:
        try:
            phone_validator(phone)
            print(f"  ✓ {phone}")
        except ValidationError as e:
            print(f"  ✗ {phone}: {str(e)}")
    
    print("\nTesting Password Strength:")
    passwords = ["Str0ng!Pass", "weak", "NoDigits!", "NOLOWERCASE123!"]
    for password in passwords:
        try:
            password_validator(password)
            score = password_validator.get_strength_score(password)
            print(f"  ✓ {password} (strength: {score:.2f})")
        except ValidationError as e:
            score = password_validator.get_strength_score(password)
            print(f"  ✗ {password} (strength: {score:.2f}): {str(e)}")
    
    print("\nTesting Composite Validator:")
    # Email OR phone required
    email_or_phone = CompositeValidator([
        EmailValidator(),
        PhoneValidator()
    ], require_all=False, severity=ValidationSeverity.WARNING)
    
    test_values = ["test@example.com", "+1-555-123-4567", "invalid"]
    for value in test_values:
        try:
            email_or_phone(value)
            print(f"  ✓ {value}")
        except ValidationError as e:
            print(f"  ✗ {value}: {str(e)}")
    
    print("\nTesting User Registration Model:")
    try:
        user = UserRegistrationModel(
            email="john@example.com",
            phone="+1-555-123-4567",
            password="Str0ng!Pass",
            website="https://johndoe.com",
            birth_date=date(1990, 1, 1)
        )
        print(f"  ✓ Valid user: {user.email}")
    except Exception as e:
        print(f"  ✗ Invalid user: {str(e)}")
    
    # Test invalid user
    try:
        invalid_user = UserRegistrationModel(
            email="invalid-email",
            phone="invalid-phone",
            password="weak",
            website="not-a-url",
            birth_date=date(2020, 1, 1)  # Too young
        )
        print(f"  ✓ This shouldn't print")
    except Exception as e:
        print(f"  ✗ Invalid user caught: {str(e)[:100]}...")

if __name__ == "__main__":
    demo_custom_validators()