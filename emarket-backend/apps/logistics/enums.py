from django.db import models
from django.utils.translation import gettext_lazy as _


class AddressType(models.TextChoices):
    """نوع آدرس"""
    HOME = 'home', _('Home')
    OFFICE = 'office', _('Office')
    WAREHOUSE = 'warehouse', _('Warehouse')
    OTHER = 'other', _('Other')


class CourierType(models.TextChoices):
    """نوع پیک"""
    INTERNAL = 'internal', _('Internal')          # پیک خودمون
    ALOPEYK = 'alopeyk', _('Alopeyk')             # الوپیک
    SNAPPBOX = 'snappbox', _('SnappBox')          # اسنپ باکس
    POST = 'post', _('Post Office')               # پست
    TIPAX = 'tipax', _('Tipax')                   # تیپاکس


class ShipmentStatus(models.TextChoices):
    """وضعیت ارسال"""
    PENDING = 'pending', _('Pending')                   # در انتظار
    ASSIGNED = 'assigned', _('Assigned to Courier')     # به پیک تخصیص داده شد
    PICKED_UP = 'picked_up', _('Picked Up')             # از انبار تحویل گرفته شد
    IN_TRANSIT = 'in_transit', _('In Transit')          # در مسیر
    DELIVERED = 'delivered', _('Delivered')             # تحویل داده شد
    RETURNED = 'returned', _('Returned')                # برگشتی
    CANCELLED = 'cancelled', _('Cancelled')


class VehicleType(models.TextChoices):
    """نوع وسیله نقلیه"""
    MOTORCYCLE = 'motorcycle', _('Motorcycle')
    CAR = 'car', _('Car')
    PICKUP = 'pickup', _('Pickup Truck')
    VAN = 'van', _('Van')
    TRUCK = 'truck', _('Truck')