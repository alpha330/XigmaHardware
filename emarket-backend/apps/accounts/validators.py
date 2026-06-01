import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_iranian_phone(value):
    """اعتبارسنجی شماره موبایل ایران"""
    pattern = r'^09\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Phone number must be in format: 09xxxxxxxxx')
        )
    return value


def validate_national_code(value):
    """اعتبارسنجی کد ملی"""
    if not value.isdigit():
        raise ValidationError(_('National code must be numeric'))
    
    if len(value) != 10:
        raise ValidationError(_('National code must be 10 digits'))
    
    # الگوریتم اعتبارسنجی کد ملی
    check = int(value[9])
    s = sum(int(value[x]) * (10 - x) for x in range(9)) % 11
    is_valid = (s < 2 and check == s) or (s >= 2 and check + s == 11)
    
    if not is_valid:
        raise ValidationError(_('Invalid national code'))
    
    return value


def validate_national_id(value):
    """اعتبارسنجی شناسه ملی (شرکت‌ها)"""
    if not value.isdigit():
        raise ValidationError(_('National ID must be numeric'))
    
    if len(value) != 11:
        raise ValidationError(_('National ID must be 11 digits'))
    
    # الگوریتم اعتبارسنجی شناسه ملی
    control = int(value[10])
    constant = 10
    total = 0
    
    for i in range(10):
        total += (int(value[i]) + constant) * (i + 1)
    
    remainder = total % 11
    remainder = remainder % 10
    
    if remainder != control:
        raise ValidationError(_('Invalid national ID'))
    
    return value


def validate_economic_code(value):
    """اعتبارسنجی کد اقتصادی"""
    if not value.isdigit():
        raise ValidationError(_('Economic code must be numeric'))
    
    if len(value) != 12:
        raise ValidationError(_('Economic code must be 12 digits'))
    
    return value


def validate_postal_code(value):
    """اعتبارسنجی کد پستی"""
    if not value.isdigit():
        raise ValidationError(_('Postal code must be numeric'))
    
    if len(value) != 10:
        raise ValidationError(_('Postal code must be 10 digits'))
    
    return value