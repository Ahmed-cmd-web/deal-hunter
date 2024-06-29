from django.db import models
from ast import literal_eval


class SourceCountries(models.TextChoices):
    EGY = {"name": "Egypt", "code": "EGY", "flag": "🇪🇬", "currency": "egp"}
