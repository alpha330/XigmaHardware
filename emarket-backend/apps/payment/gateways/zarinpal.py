"""Backward-compatible import for the active REST-based ZarinPal gateway."""

from apps.payment.services.zarinpal import ZarinPalGateway


__all__ = ['ZarinPalGateway']
