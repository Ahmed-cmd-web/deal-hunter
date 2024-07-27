from django.db import models


class TargetCountries(models.TextChoices):
    KSA = {"name": "Saudi Arabia", "code": "KSA", "flag": "🇸🇦", "currency": "sar"}
    UAE = {
        "name": "United Arab Emirates",
        "code": "UAE",
        "flag": "🇦🇪",
        "currency": "aed",
    }
    DE = {"name": "Germany", "code": "DE", "flag": "🇩🇪", "currency": "eur"}
    FR = {"name": "France", "code": "FR", "flag": "🇫🇷", "currency": "eur"}
    ES = {"name": "Spain", "code": "ES", "flag": "🇪🇸", "currency": "eur"}
    IT = {"name": "Italy", "code": "IT", "flag": "🇮🇹", "currency": "eur"}