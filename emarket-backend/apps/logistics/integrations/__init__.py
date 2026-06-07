"""
پکیج یکپارچگی با سرویس‌های پیک خارجی

سرویس‌های پشتیبانی شده:
- Alopeyk (الوپیک)
- SnappBox (اسنپ باکس)
- Post (پست - آینده)
- Tipax (تیپاکس - آینده)
"""

from .base import BaseCourierAPI
from .alopeyk import AlopeykAPI
from .snappbox import SnappBoxAPI

__all__ = [
    'BaseCourierAPI',
    'AlopeykAPI',
    'SnappBoxAPI',
]