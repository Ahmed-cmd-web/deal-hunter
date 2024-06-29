from enum import Enum
from django.db import models


class TargetCountries(models.TextChoices):
    KSA = {"name": "Saudi Arabia", "code": "KSA", "flag": "🇸🇦", "currency": "sar"}
    UAE = {
        "name": "United Arab Emirates",
        "code": "UAE",
        "flag": "🇦🇪",
        "currency": "aed",
    }
